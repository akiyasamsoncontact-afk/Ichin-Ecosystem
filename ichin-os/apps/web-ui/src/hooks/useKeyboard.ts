import { useEffect } from 'react'

type KeyHandler = Record<string, () => void>

export function useKeyboard(handlers: KeyHandler) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const key = e.key === ' ' ? 'Space' : e.key
      const handler = handlers[key]
      if (handler) {
        e.preventDefault()
        handler()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handlers])
}
