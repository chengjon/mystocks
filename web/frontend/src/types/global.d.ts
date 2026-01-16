/**
 * 全局类型声明
 *
 * 为自动导入的Element Plus API添加类型声明
 */

// Element Plus全局API类型声明
declare global {
    const ElMessage: {
        success(message: string): void
        warning(message: string): void
        info(message: string): void
        error(message: string): void
    }

    const ElMessageBox: {
        alert(message: string): Promise<void>
        confirm(message: string): Promise<void>
        prompt(message: string): Promise<string>
    }

    const ElNotification: {
        success(message: string): void
        warning(message: string): void
        info(message: string): void
        error(message: string): void
    }

    const ElLoading: {
        show(target?: string | HTMLElement): void
        hide(target?: string | HTMLElement): void
    }
}

export {}
