/**
 * 第三方库类型声明补充
 *
 * 为缺少官方类型声明的第三方库提供基本类型定义
 */

declare module 'html2canvas' {
    interface Html2CanvasOptions {
        backgroundColor?: string
        scale?: number
        width?: number
        height?: number
        useCORS?: boolean
        allowTaint?: boolean
        logging?: boolean
    }

    interface Html2Canvas {
        (element: HTMLElement, options?: Html2CanvasOptions): Promise<HTMLCanvasElement>
    }

    const html2canvas: Html2Canvas
    export default html2canvas
}

declare module 'file-saver' {
    function saveAs(blob: Blob, filename?: string): void

    export = saveAs
    export { saveAs }
}

declare module 'jspdf' {
    interface jsPDFOptions {
        orientation?: 'p' | 'portrait' | 'l' | 'landscape'
        unit?: 'pt' | 'px' | 'in' | 'mm'
        format?: string
    }

    class jsPDF {
        constructor(options?: jsPDFOptions)
        internal: {
            pageSize: {
                getWidth(): number
                getHeight(): number
            }
        }
        save(filename?: string): void
        addImage(
            imageData: string | HTMLCanvasElement,
            format: string,
            x: number,
            y: number,
            w: number,
            h: number
        ): void
        text(text: string, x: number, y: number, options?: any): void
    }

    export default jsPDF
    export { jsPDF }
}

declare module 'xlsx' {
    interface WorkBook {
        SheetNames: string[]
        Sheets: { [key: string]: any }
    }

    interface XLSXUtils {
        book_new(): WorkBook
        json_to_sheet(data: any[]): any
        book_append_sheet(wb: WorkBook, ws: any, name: string): void
    }

    interface XLSXExport {
        utils: XLSXUtils
        writeFile(workbook: any, filename: string): void
    }

    const XLSX: XLSXExport

    export default XLSX
}
