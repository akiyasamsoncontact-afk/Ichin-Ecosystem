import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useUIStore } from '../../stores/uiStore'

type Mood = 'calm' | 'neutral' | 'focus' | 'deep_focus'
type Intensity = 'subtle' | 'balanced' | 'active'

const MOODS: { value: Mood; label: string; desc: string; color: string }[] = [
  { value: 'calm', label: 'Calm', desc: 'Soft blues and gentle gradients — for relaxed focus', color: '#4A9EFF' },
  { value: 'neutral', label: 'Neutral', desc: 'Balanced grays — clean and minimal', color: '#9E9E9E' },
  { value: 'focus', label: 'Focus', desc: 'Deep greens — high concentration mode', color: '#00E676' },
  { value: 'deep_focus', label: 'Deep Focus', desc: 'Dark ambers — maximum immersion', color: '#FFB300' },
]

const INTENSITIES: { value: Intensity; label: string; desc: string }[] = [
  { value: 'subtle', label: 'Subtle', desc: 'Minimal AI suggestions, only when asked' },
  { value: 'balanced', label: 'Balanced', desc: 'Proactive suggestions, respects context' },
  { value: 'active', label: 'Active', desc: 'Always-on AI assistance, constant feedback' },
]

const GOALS = [
  { id: 'study', label: 'Study', desc: 'Master new subjects, prepare for exams, research deeply' },
  { id: 'coding', label: 'Coding', desc: 'Build software, debug, learn frameworks' },
  { id: 'learning', label: 'Learning', desc: 'Explore topics, take courses, skill development' },
  { id: 'personal', label: 'Life', desc: 'Organize tasks, manage projects, daily productivity' },
]

const slideVariants = {
  enter: (d: number) => ({ x: d > 0 ? 300 : -300, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (d: number) => ({ x: d > 0 ? -300 : 300, opacity: 0 }),
}

export default function OnboardingFlow() {
  const [step, setStep] = useState(0)
  const [direction, setDirection] = useState(1)
  const [name, setName] = useState('')
  const [goals, setGoals] = useState<string[]>([])
  const [mood, setMood] = useState<Mood>('neutral')
  const [intensity, setIntensity] = useState<Intensity>('balanced')
  const completeOnboarding = useUIStore((s) => s.completeOnboarding)
  const setAmbientMode = useUIStore((s) => s.setAmbientMode)

  const next = useCallback(() => {
    setDirection(1)
    setStep((s) => Math.min(s + 1, 2))
  }, [])

  const prev = useCallback(() => {
    setDirection(-1)
    setStep((s) => Math.max(s - 1, 0))
  }, [])

  const finish = useCallback(() => {
    localStorage.setItem('ichin-user-name', name)
    localStorage.setItem('ichin-goals', JSON.stringify(goals))
    localStorage.setItem('ichin-mood', mood)
    localStorage.setItem('ichin-intensity', intensity)
    setAmbientMode(mood)
    completeOnboarding()
  }, [name, goals, mood, intensity])

  return (
    <div className="h-full w-full flex items-center justify-center bg-bg">
      <div className="w-full max-w-lg">
        <div className="flex justify-center gap-2 mb-12">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`h-1 rounded-full transition-all duration-500 ${i === step ? 'w-12 bg-white/60' : 'w-3 bg-white/10'}`}
            />
          ))}
        </div>

        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={step}
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.35, ease: 'easeInOut' }}
          >
            {step === 0 && (
              <div className="space-y-8">
                <div className="text-center space-y-2">
                  <h1 className="text-2xl font-light text-white">Welcome to ICHIN OS</h1>
                  <p className="text-sm text-white/40">Let's set up your operating system</p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs text-white/40 uppercase tracking-wider">What should we call you?</label>
                  <input
                    autoFocus
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name..."
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/20 focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>

                <div className="space-y-3">
                  <label className="text-xs text-white/40 uppercase tracking-wider">What are you building your OS for?</label>
                  <div className="grid grid-cols-2 gap-3">
                    {GOALS.map((g) => (
                      <button
                        key={g.id}
                        onClick={() => setGoals((p) => p.includes(g.id) ? p.filter((x) => x !== g.id) : [...p, g.id])}
                        className={`p-4 rounded-xl text-left transition-all ${
                          goals.includes(g.id)
                            ? 'bg-white/10 border border-white/20'
                            : 'bg-white/5 border border-transparent hover:bg-white/10'
                        }`}
                      >
                        <div className="text-sm font-medium text-white/80">{g.label}</div>
                        <div className="text-xs text-white/30 mt-1">{g.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={next}
                    disabled={!name || goals.length === 0}
                    className="px-6 py-2.5 rounded-xl bg-white/10 text-white text-sm hover:bg-white/15 disabled:opacity-30 transition-all"
                  >
                    Continue
                  </button>
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-8">
                <div className="text-center space-y-2">
                  <h1 className="text-2xl font-light text-white">Workspace Shaping</h1>
                  <p className="text-sm text-white/40">AI will auto-configure your spaces</p>
                </div>

                <div className="space-y-3">
                  {goals.map((g) => {
                    const goal = GOALS.find((x) => x.id === g)
                    return (
                      <div key={g} className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center gap-4">
                        <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-white/60 text-sm">
                          {goal?.label[0]}
                        </div>
                        <div>
                          <div className="text-sm text-white/80">{goal?.label} Space</div>
                          <div className="text-xs text-white/30">AI is configuring your environment...</div>
                        </div>
                      </div>
                    )
                  })}
                </div>

                <p className="text-xs text-white/20 text-center">
                  Your workspaces will be tailored to your goals with pre-loaded tools and AI agents.
                </p>

                <div className="flex justify-between">
                  <button onClick={prev} className="px-6 py-2.5 rounded-xl text-white/40 hover:text-white/60 transition-all">
                    Back
                  </button>
                  <button onClick={next} className="px-6 py-2.5 rounded-xl bg-white/10 text-white text-sm hover:bg-white/15 transition-all">
                    Continue
                  </button>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-8">
                <div className="text-center space-y-2">
                  <h1 className="text-2xl font-light text-white">Ambient Setup</h1>
                  <p className="text-sm text-white/40">Choose your visual and AI style</p>
                </div>

                <div className="space-y-4">
                  <label className="text-xs text-white/40 uppercase tracking-wider">Visual Mood</label>
                  <div className="grid grid-cols-2 gap-3">
                    {MOODS.map((m) => (
                      <button
                        key={m.value}
                        onClick={() => setMood(m.value)}
                        className={`p-4 rounded-xl transition-all ${
                          mood === m.value
                            ? 'border'
                            : 'bg-white/5 hover:bg-white/10 border border-transparent'
                        }`}
                        style={mood === m.value ? { borderColor: m.color, backgroundColor: m.color + '15' } : {}}
                      >
                        <div className="text-sm font-medium text-white/80">{m.label}</div>
                        <div className="text-xs text-white/30 mt-1">{m.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="text-xs text-white/40 uppercase tracking-wider">AI Intervention Intensity</label>
                  <div className="flex gap-3">
                    {INTENSITIES.map((i) => (
                      <button
                        key={i.value}
                        onClick={() => setIntensity(i.value)}
                        className={`flex-1 p-4 rounded-xl text-center transition-all ${
                          intensity === i.value
                            ? 'bg-white/10 border border-white/20'
                            : 'bg-white/5 hover:bg-white/10 border border-transparent'
                        }`}
                      >
                        <div className="text-sm font-medium text-white/80">{i.label}</div>
                        <div className="text-xs text-white/30 mt-1">{i.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex justify-between">
                  <button onClick={prev} className="px-6 py-2.5 rounded-xl text-white/40 hover:text-white/60 transition-all">
                    Back
                  </button>
                  <button
                    onClick={finish}
                    className="px-8 py-2.5 rounded-xl bg-white/15 text-white text-sm hover:bg-white/20 transition-all"
                  >
                    Enter ICHIN OS
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
