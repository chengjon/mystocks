"""
Data Export API
数据导出API

Provides endpoints to export fund flow data to Excel/CSV formats.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, Literal
from datetime import datetime
import pandas as pd
import structlog
import io

from app.core.security import get_current_user, User
from app.api.market_v3 import get_fund_flow_data

router = APIRouter()
logger = structlog.get_logger()


@router.get("/fund-flow/export")
async def export_fund_flow_data(
    format: Literal["excel", "csv"] = Query(
        "excel", description="导出格式: excel 或 csv"
    ),
    trade_date: Optional[str] = Query(
        None, description="交易日期 YYYY-MM-DD，默认最近一个交易日"
    ),
    industry_type: str = Query(
        "csrc", regex="^(csrc|sw_l1|sw_l2)$", description="行业分类标准"
    ),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    current_user: User = Depends(get_current_user),
):
    """
    导出资金流向数据到Excel或CSV

    支持格式:
    - excel: .xlsx格式 (支持多sheet, 格式化)
    - csv: .csv格式 (纯文本, 兼容性好)

    Returns:
        StreamingResponse with file download
    """
    try:
        logger.info(
            f"Export request by user: {current_user.username}",
            format=format,
            industry_type=industry_type,
            limit=limit,
        )

        # 调用现有API获取数据
        result = await get_fund_flow_data(
            trade_date=trade_date,
            industry_type=industry_type,
            limit=limit,
            current_user=current_user,
        )

        if not result.get("success") or not result.get("data"):
            raise HTTPException(status_code=404, detail="没有可导出的数据")

        data = result["data"]
        df = pd.DataFrame(data)

        # 数据格式化
        if not df.empty:
            # 列名中文化
            column_mapping = {
                "industry_name": "行业名称",
                "industry_type": "行业类型",
                "net_inflow": "净流入(亿元)",
                "main_inflow": "主力净流入(亿元)",
                "retail_inflow": "散户净流入(亿元)",
                "trade_date": "交易日期",
                "total_inflow": "总流入(亿元)",
                "total_outflow": "总流出(亿元)",
            }
            df = df.rename(columns=column_mapping)

            # 数值格式化 (保留2位小数)
            numeric_cols = [
                "净流入(亿元)",
                "主力净流入(亿元)",
                "散户净流入(亿元)",
                "总流入(亿元)",
                "总流出(亿元)",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].round(2)

            # 行业类型映射
            industry_type_map = {
                "csrc": "证监会行业",
                "sw_l1": "申万一级",
                "sw_l2": "申万二级",
            }
            if "行业类型" in df.columns:
                df["行业类型"] = df["行业类型"].map(industry_type_map)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        industry_type_name = {"csrc": "CSRC", "sw_l1": "SW_L1", "sw_l2": "SW_L2"}.get(
            industry_type, industry_type
        )
        filename = f"fund_flow_{industry_type_name}_{timestamp}"

        # 导出为Excel或CSV
        if format == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="资金流向", index=False)

                # 获取worksheet并设置列宽
                worksheet = writer.sheets["资金流向"]
                for idx, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).apply(len).max(), len(col))
                    # 中文字符宽度调整
                    adjusted_width = min(max_length * 1.5 + 2, 50)
                    worksheet.column_dimensions[chr(65 + idx)].width = adjusted_width

            output.seek(0)
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename_with_ext = f"{filename}.xlsx"

        else:  # CSV
            output = io.StringIO()
            df.to_csv(output, index=False, encoding="utf-8-sig")  # BOM for Excel
            output.seek(0)
            # Convert StringIO to BytesIO
            bytes_output = io.BytesIO(output.getvalue().encode("utf-8-sig"))
            output = bytes_output
            media_type = "text/csv; charset=utf-8"
            filename_with_ext = f"{filename}.csv"

        logger.info(
            f"Export completed: {filename_with_ext}",
            records=len(df),
            user=current_user.username,
        )

        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename_with_ext}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="数据导出失败，请稍后重试")
