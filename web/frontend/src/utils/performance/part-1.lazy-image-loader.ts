export class LazyImageLoader {
  private static observer?: IntersectionObserver
  private static images = new Map<HTMLImageElement, string>()

  /**
   * Setup lazy loading
   */
  static setup(): void {
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement
              const src = this.images.get(img)

              if (src) {
                img.src = src
                img.classList.add('loaded')
                this.images.delete(img)
                this.observer?.unobserve(img)
              }
            }
          })
        },
        {
          rootMargin: '50px 0px'
        }
      )
    }
  }

  /**
   * Observe image for lazy loading
   */
  static observe(img: HTMLImageElement, src: string): void {
    if (!this.observer) {
      this.setup()
    }

    img.classList.add('lazy-loading')

    if (this.observer) {
      this.images.set(img, src)
      this.observer.observe(img)
    } else {
      img.src = src
    }
  }

  /**
   * Unobserve image
   */
  static unobserve(img: HTMLImageElement): void {
    if (this.observer) {
      this.observer.unobserve(img)
    }
    this.images.delete(img)
  }

  /**
   * Disconnect observer
   */
  static disconnect(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = undefined
    }
    this.images.clear()
  }
}
