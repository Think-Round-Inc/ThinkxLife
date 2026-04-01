'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Home, Maximize2, Minimize2 } from 'lucide-react'

export default function ExteriorSpacesPage() {
  // Your Figma prototype embed URL (optimized fit - no sidebar, no UI, proper scaling)
  const figmaEmbedUrl = "https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Fproto%2FmAq1KGpFlEMPBiPRCEEbNy%2FExterior-Spaces%3Fnode-id%3D228-981%26p%3Df%26t%3DPkpHrsBjZLwUuO6f-0%26scaling%3Dscale-down%26content-scaling%3Dfixed%26page-id%3D0%253A1%26starting-point-node-id%3D228%253A981%26show-proto-sidebar%3D0%26hide-ui%3D1"

  // State for showing controls
  const [showControls, setShowControls] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [iframeStyle, setIframeStyle] = useState({})
  const [hideTimer, setHideTimer] = useState<NodeJS.Timeout | null>(null)
  const [isHoveringControls, setIsHoveringControls] = useState(false)

  // Set page title
  useEffect(() => {
    document.title = 'Exterior Spaces | ThinkLife'
  }, [])

  // Set basic iframe styling
  useEffect(() => {
    setIframeStyle({
      border: 'none',
      marginTop: 0,
      marginRight: 0,
      marginBottom: 0,
      marginLeft: 0,
      padding: 0,
      overflow: 'hidden',
      width: '100%',
      height: '100%'
    })
  }, [])

  // Enter browser fullscreen mode
  const enterFullscreen = async () => {
    try {
      const element = document.documentElement as HTMLElement & {
        webkitRequestFullscreen?: () => Promise<void>
        msRequestFullscreen?: () => Promise<void>
      }
      
      if (element.requestFullscreen) {
        await element.requestFullscreen()
      } else if (element.webkitRequestFullscreen) {
        await element.webkitRequestFullscreen()
      } else if (element.msRequestFullscreen) {
        await element.msRequestFullscreen()
      }
    } catch (error) {
      console.log('Fullscreen request failed:', error)
      // Fail silently - user can still use the page normally
    }
  }

  // Exit browser fullscreen mode
  const exitFullscreen = async () => {
    try {
      const doc = document as Document & {
        webkitExitFullscreen?: () => Promise<void>
        msExitFullscreen?: () => Promise<void>
      }
      
      if (doc.exitFullscreen) {
        await doc.exitFullscreen()
      } else if (doc.webkitExitFullscreen) {
        await doc.webkitExitFullscreen()
      } else if (doc.msExitFullscreen) {
        await doc.msExitFullscreen()
      }
    } catch (error) {
      console.log('Exit fullscreen failed:', error)
      // Fail silently
    }
  }

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      const doc = document as Document & {
        webkitFullscreenElement?: Element
        msFullscreenElement?: Element
      }
      setIsFullscreen(!!(doc.fullscreenElement || doc.webkitFullscreenElement || doc.msFullscreenElement))
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('msfullscreenchange', handleFullscreenChange)

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
      document.removeEventListener('msfullscreenchange', handleFullscreenChange)
    }
  }, [])

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (hideTimer) {
        clearTimeout(hideTimer)
      }
    }
  }, [hideTimer])

  // Auto-hide controls after 5 seconds initially
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!isHoveringControls) {
        setShowControls(false)
      }
    }, 5000)

    return () => clearTimeout(timer)
  }, [])

  // Stable hover handling
  const handleControlAreaEnter = () => {
    console.log('Control area entered')
    if (hideTimer) {
      clearTimeout(hideTimer)
      setHideTimer(null)
    }
    setIsHoveringControls(true)
    setShowControls(true)
  }

  const handleControlAreaLeave = () => {
    console.log('Control area left')
    setIsHoveringControls(false)
    // Only hide if we're not hovering over controls
    const timer = setTimeout(() => {
      console.log('Hiding controls after delay')
      setShowControls(false)
    }, 500) // Increased delay for better UX
    setHideTimer(timer)
  }

  return (
    <div className="w-full h-full relative">
      {/* Combined Control Area - Full width top strip */}
      <div 
        className="absolute top-0 left-0 w-full h-20 z-[60] bg-transparent"
        onMouseEnter={handleControlAreaEnter}
        onMouseLeave={handleControlAreaLeave}
        style={{ 
          pointerEvents: 'auto',
          // Uncomment for debugging: backgroundColor: 'rgba(255,0,0,0.1)'
        }}
      >
        {/* Floating Controls */}
        <AnimatePresence>
          {showControls && (
            <motion.div
              className="absolute top-4 left-4 z-[70] flex items-center gap-3 pointer-events-auto"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
            {/* Home Button */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="pointer-events-auto"
            >
              <Link
                href="/exterior-spaces"
                onClick={(e) => {
                  console.log('Home button clicked')
                  // Exit fullscreen before navigating home
                  if (isFullscreen) {
                    exitFullscreen()
                  }
                }}
                className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-all duration-200 border border-white/20 cursor-pointer"
                style={{ pointerEvents: 'auto' }}
              >
                <Home className="h-4 w-4" />
                <span className="hidden sm:inline">Home</span>
              </Link>
            </motion.div>

            {/* Fullscreen Toggle */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="pointer-events-auto"
            >
              <button
                onClick={(e) => {
                  console.log('Fullscreen button clicked', { isFullscreen })
                  e.preventDefault()
                  e.stopPropagation()
                  if (isFullscreen) {
                    exitFullscreen()
                  } else {
                    enterFullscreen()
                  }
                }}
                className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-all duration-200 border border-white/20 cursor-pointer"
                style={{ pointerEvents: 'auto' }}
              >
                {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                <span className="hidden sm:inline">{isFullscreen ? 'Exit' : 'Fullscreen'}</span>
              </button>
            </motion.div>

            {/* Page Title */}
            <motion.div
              className="bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-lg border border-white/20"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <span className="font-medium">Exterior Spaces Prototype</span>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      </div>

      {/* Instructions (shown briefly) */}
      <AnimatePresence>
        {showControls && (
          <motion.div
            className="absolute bottom-4 left-4 z-[70] text-white/70 text-sm pointer-events-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <div className="bg-black/30 backdrop-blur-sm px-3 py-2 rounded-lg border border-white/10">
              {isFullscreen 
                ? "Press ESC or click Exit to exit fullscreen • Hover top-left area to show controls" 
                : "Click Fullscreen for immersive experience • Hover top-left area to show controls"
              }
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Fullscreen Figma Prototype */}
      <motion.iframe
        src={figmaEmbedUrl}
        className="absolute inset-0 z-[40]"
        allowFullScreen
        title="Exterior Spaces Prototype"
        style={{
          ...iframeStyle,
          pointerEvents: 'auto'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      />

      {/* Loading Overlay */}
      <motion.div
        className="absolute inset-0 bg-black flex items-center justify-center pointer-events-none"
        initial={{ opacity: 1 }}
        animate={{ opacity: 0 }}
        transition={{ duration: 0.5, delay: 1 }}
      >
        <div className="text-white text-center">
          <motion.div
            className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
          />
          <motion.p
            className="text-white/70"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            Loading Exterior Spaces Prototype...
          </motion.p>
        </div>
      </motion.div>
    </div>
  )
}
