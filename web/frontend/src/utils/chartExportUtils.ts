/**
 * Chart Export and Sharing Utilities
 *
 * Provides comprehensive export functionality for charts including PNG, SVG, PDF formats
 * and sharing capabilities with data serialization and embed codes.
 */

import type { EChartsOption } from 'echarts'
import html2canvas from 'html2canvas'
import { saveAs } from 'file-saver'

// ================ 导出配置 ================

export interface ExportConfig {
    format: 'png' | 'svg' | 'pdf' | 'json' | 'csv'
    filename?: string
    width?: number
    height?: number
    quality?: number // 0-1 for PNG
    backgroundColor?: string
    includeTitle?: boolean
    includeLegend?: boolean
    scale?: number
}

export interface ShareConfig {
    platform: 'link' | 'embed' | 'image' | 'data'
    title?: string
    description?: string
    tags?: string[]
    privacy?: 'public' | 'private' | 'unlisted'
}

// ================ 图片导出工具 ================

export class ChartImageExporter {
    /**
     * 导出为PNG格式
     */
    static async exportToPNG(chartElement: HTMLElement, config: ExportConfig = { format: 'png' }): Promise<void> {
        try {
            const canvas = await html2canvas(chartElement, {
                backgroundColor: config.backgroundColor || '#ffffff',
                scale: config.scale || 2, // 更高分辨率
                width: config.width,
                height: config.height,
                useCORS: true,
                allowTaint: false
            })

            canvas.toBlob(
                (blob: any) => {
                    if (blob) {
                        const filename = config.filename || `chart-${Date.now()}.png`
                        saveAs(blob, filename)
                    }
                },
                'image/png',
                config.quality || 0.9
            )
        } catch (error) {
            console.error('PNG导出失败:', error)
            throw new Error('Failed to export chart as PNG')
        }
    }

    /**
     * 导出为SVG格式 (通过ECharts)
     */
    static exportToSVG(echartsInstance: any, config: ExportConfig = { format: 'svg' }): void {
        try {
            const svgData = echartsInstance.getDataURL({
                type: 'svg',
                pixelRatio: config.scale || 2,
                backgroundColor: config.backgroundColor
            })

            const link = document.createElement('a')
            link.download = config.filename || `chart-${Date.now()}.svg`
            link.href = svgData
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
        } catch (error) {
            console.error('SVG导出失败:', error)
            throw new Error('Failed to export chart as SVG')
        }
    }

    /**
     * 导出为PDF格式
     */
    static async exportToPDF(chartElement: HTMLElement, config: ExportConfig = { format: 'pdf' }): Promise<void> {
        try {
            // 动态导入jsPDF
            const { jsPDF } = await import('jspdf')

            const canvas = await html2canvas(chartElement, {
                backgroundColor: config.backgroundColor || '#ffffff',
                scale: config.scale || 2,
                width: config.width,
                height: config.height
            })

            const imgData = canvas.toDataURL('image/png')
            const pdf = new jsPDF({
                orientation: config.width && config.height && config.width > config.height ? 'landscape' : 'portrait',
                unit: 'mm',
                format: 'a4'
            })

            const pdfWidth = pdf.internal.pageSize.getWidth()
            const pdfHeight = pdf.internal.pageSize.getHeight()

            // 计算图片尺寸以适应PDF页面
            const imgAspectRatio = canvas.width / canvas.height
            let imgWidth = pdfWidth - 20 // 左右边距
            let imgHeight = imgWidth / imgAspectRatio

            if (imgHeight > pdfHeight - 20) {
                imgHeight = pdfHeight - 20
                imgWidth = imgHeight * imgAspectRatio
            }

            // 居中图片
            const x = (pdfWidth - imgWidth) / 2
            const y = (pdfHeight - imgHeight) / 2

            pdf.addImage(imgData, 'PNG', x, y, imgWidth, imgHeight)

            const filename = config.filename || `chart-${Date.now()}.pdf`
            pdf.save(filename)
        } catch (error) {
            console.error('PDF导出失败:', error)
            throw new Error('Failed to export chart as PDF')
        }
    }
}

// ================ 数据导出工具 ================

export class ChartDataExporter {
    /**
     * 导出为JSON格式
     */
    static exportToJSON(data: any, config: ExportConfig = { format: 'json' }): void {
        try {
            const jsonString = JSON.stringify(data, null, 2)
            const blob = new Blob([jsonString], { type: 'application/json' })
            const filename = config.filename || `chart-data-${Date.now()}.json`
            saveAs(blob, filename)
        } catch (error) {
            console.error('JSON导出失败:', error)
            throw new Error('Failed to export data as JSON')
        }
    }

    /**
     * 导出为CSV格式
     */
    static exportToCSV(data: any[], config: ExportConfig = { format: 'csv' }): void {
        try {
            if (!Array.isArray(data) || data.length === 0) {
                throw new Error('Data must be a non-empty array')
            }

            // 获取所有可能的列
            const columns = new Set<string>()
            data.forEach(item => {
                if (typeof item === 'object' && item !== null) {
                    Object.keys(item).forEach(key => columns.add(key))
                }
            })

            const headers = Array.from(columns)

            // 创建CSV内容
            const csvRows = [
                headers.join(','), // 表头
                ...data.map(row => {
                    return headers
                        .map(header => {
                            const value = row[header]
                            // 处理包含逗号或引号的值
                            if (
                                typeof value === 'string' &&
                                (value.includes(',') || value.includes('"') || value.includes('\n'))
                            ) {
                                return `"${value.replace(/"/g, '""')}"`
                            }
                            return value || ''
                        })
                        .join(',')
                })
            ]

            const csvContent = csvRows.join('\n')
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
            const filename = config.filename || `chart-data-${Date.now()}.csv`
            saveAs(blob, filename)
        } catch (error) {
            console.error('CSV导出失败:', error)
            throw new Error('Failed to export data as CSV')
        }
    }

    /**
     * 导出为Excel格式
     */
    static async exportToExcel(data: any[], config: ExportConfig = { format: 'csv' }): Promise<void> {
        try {
            // 动态导入xlsx库
            const XLSX = (await import('xlsx')) as any

            // 创建工作簿
            const wb = XLSX.utils.book_new()

            // 将数据转换为工作表
            const ws = XLSX.utils.json_to_sheet(data)

            // 添加工作表到工作簿
            XLSX.utils.book_append_sheet(wb, ws, 'Chart Data')

            // 导出为Excel文件
            const filename = config.filename || `chart-data-${Date.now()}.xlsx`
            XLSX.writeFile(wb, filename)
        } catch (error) {
            console.error('Excel导出失败:', error)
            throw new Error('Failed to export data as Excel')
        }
    }
}

// ================ 分享工具 ================

export class ChartShareManager {
    /**
     * 生成分享链接
     */
    static generateShareLink(chartConfig: EChartsOption, config: ShareConfig): string {
        try {
            // 序列化图表配置
            const serializedConfig = btoa(
                JSON.stringify({
                    config: chartConfig,
                    metadata: {
                        title: config.title,
                        description: config.description,
                        tags: config.tags,
                        timestamp: Date.now()
                    }
                })
            )

            // 生成分享URL
            const baseUrl = window.location.origin
            const shareUrl = `${baseUrl}/shared-chart?data=${encodeURIComponent(serializedConfig)}`

            return shareUrl
        } catch (error) {
            console.error('生成分享链接失败:', error)
            throw new Error('Failed to generate share link')
        }
    }

    /**
     * 生成嵌入代码
     */
    static generateEmbedCode(chartConfig: EChartsOption, config: ShareConfig): string {
        try {
            const serializedConfig = btoa(JSON.stringify(chartConfig))

            const embedCode = `
<div id="embedded-chart" style="width: 100%; height: 400px;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
  const chart = echarts.init(document.getElementById('embedded-chart'));
  const config = JSON.parse(atob('${serializedConfig}'));
  chart.setOption(config);
</script>
      `.trim()

            return embedCode
        } catch (error) {
            console.error('生成嵌入代码失败:', error)
            throw new Error('Failed to generate embed code')
        }
    }

    /**
     * 分享到社交媒体
     */
    static shareToSocialMedia(platform: 'twitter' | 'linkedin' | 'facebook', url: string, config: ShareConfig): void {
        const encodedUrl = encodeURIComponent(url)
        const encodedTitle = encodeURIComponent(config.title || 'Interactive Chart')
        const encodedDescription = encodeURIComponent(config.description || '')

        let shareUrl = ''

        switch (platform) {
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`
                break
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`
                break
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`
                break
        }

        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400')
        }
    }

    /**
     * 导出分享配置
     */
    static exportShareConfig(chartConfig: EChartsOption, config: ShareConfig): any {
        return {
            chartConfig,
            shareConfig: config,
            exportTimestamp: Date.now(),
            version: '1.0'
        }
    }
}

// ================ 批量导出管理器 ================

export class BatchExportManager {
    private exportQueue: Array<{
        id: string
        config: ExportConfig
        element: HTMLElement
        echartsInstance?: any
        resolve: (value: void) => void
        reject: (reason: any) => void
    }> = []

    private isProcessing = false

    /**
     * 添加导出任务到队列
     */
    addToQueue(config: ExportConfig, element: HTMLElement, echartsInstance?: any): Promise<void> {
        return new Promise((resolve, reject) => {
            const id = `export-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

            this.exportQueue.push({
                id,
                config,
                element,
                echartsInstance,
                resolve,
                reject
            })

            this.processQueue()
        })
    }

    /**
     * 处理导出队列
     */
    private async processQueue(): Promise<void> {
        if (this.isProcessing || this.exportQueue.length === 0) return

        this.isProcessing = true

        while (this.exportQueue.length > 0) {
            const task = this.exportQueue.shift()
            if (!task) continue

            try {
                await this.executeExport(task)
                task.resolve()
            } catch (error) {
                task.reject(error)
            }

            // 添加延迟避免浏览器过载
            await new Promise(resolve => setTimeout(resolve, 500))
        }

        this.isProcessing = false
    }

    /**
     * 执行单个导出任务
     */
    private async executeExport(task: (typeof this.exportQueue)[0]): Promise<void> {
        const { config, element, echartsInstance } = task

        switch (config.format) {
            case 'png':
                await ChartImageExporter.exportToPNG(element, config)
                break
            case 'svg':
                if (echartsInstance) {
                    ChartImageExporter.exportToSVG(echartsInstance, config)
                } else {
                    throw new Error('SVG export requires ECharts instance')
                }
                break
            case 'pdf':
                await ChartImageExporter.exportToPDF(element, config)
                break
            case 'json':
                ChartDataExporter.exportToJSON({ config, element }, config)
                break
            case 'csv':
                ChartDataExporter.exportToCSV([{ config, element }], config)
                break
            default:
                throw new Error(`Unsupported export format: ${config.format}`)
        }
    }

    /**
     * 获取队列状态
     */
    getQueueStatus(): {
        queueLength: number
        isProcessing: boolean
    } {
        return {
            queueLength: this.exportQueue.length,
            isProcessing: this.isProcessing
        }
    }

    /**
     * 清空队列
     */
    clearQueue(): void {
        this.exportQueue.forEach(task => {
            task.reject(new Error('Export cancelled'))
        })
        this.exportQueue = []
    }
}
