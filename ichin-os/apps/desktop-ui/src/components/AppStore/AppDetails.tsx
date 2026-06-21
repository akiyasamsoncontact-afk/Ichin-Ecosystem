import { motion } from 'framer-motion'
import { Star, Download, X, Shield, Sparkles, Layers, ChevronLeft } from 'lucide-react'
import type { AppManifest } from '../../types'

interface AppDetailsProps {
  app: AppManifest
  installed: boolean
  onInstall: () => void
  onClose: () => void
}

export default function AppDetails({ app, installed, onInstall, onClose }: AppDetailsProps) {
  return (
    <motion.div
      className="absolute inset-0 bg-bg/90 backdrop-blur-md z-10"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
    >
      <div className="p-4 space-y-4">
        <button onClick={onClose} className="flex items-center gap-1 text-xs text-white/40 hover:text-white/60">
          <ChevronLeft size={14} /> Back
        </button>

        <div className="space-y-1">
          <h2 className="text-lg font-light text-white/80">{app.name}</h2>
          <p className="text-xs text-white/30">{app.description}</p>
        </div>

        <div className="flex items-center gap-4 text-xs text-white/40">
          <div className="flex items-center gap-1">
            <Star size={12} className="text-yellow-500" />
            {app.rating}
          </div>
          <div>v{app.version}</div>
          <div>{app.author}</div>
          {app.aiTested && (
            <span className="flex items-center gap-1 text-accent-coding">
              <Sparkles size={12} /> AI Tested
            </span>
          )}
        </div>

        <div className="glass rounded-xl p-4 space-y-3">
          <h3 className="text-xs uppercase tracking-wider text-white/30">Permissions</h3>
          {app.permissions.length > 0 ? app.permissions.map((p, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-white/50">
              <Shield size={12} className="text-white/20" />
              {p.name} — {p.description}
            </div>
          )) : (
            <p className="text-xs text-white/20">No special permissions required</p>
          )}
        </div>

        <div className="glass rounded-xl p-4 space-y-3">
          <h3 className="text-xs uppercase tracking-wider text-white/30">Workspace Integration</h3>
          <div className="flex gap-2">
            {app.workspaceIntegration.map((ws) => (
              <span key={ws} className="text-[10px] px-2 py-1 rounded-full bg-white/5 text-white/40 capitalize">
                {ws}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 mt-4">
          <div className="flex items-center gap-2 text-xs text-white/30">
            <Layers size={12} />
            AI Compatibility: {app.aiCompatibility}%
          </div>
        </div>

        <button
          onClick={onInstall}
          className={`w-full py-2.5 rounded-xl text-sm transition-all ${
            installed
              ? 'bg-white/10 text-white/60 hover:bg-white/15'
              : 'bg-accent-coding/15 text-accent-coding hover:bg-accent-coding/25'
          }`}
        >
          {installed ? 'Uninstall' : 'Install'}
        </button>
      </div>
    </motion.div>
  )
}
