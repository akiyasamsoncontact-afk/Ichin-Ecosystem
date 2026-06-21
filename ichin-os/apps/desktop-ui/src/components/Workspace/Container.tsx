import { AnimatePresence, motion } from 'framer-motion'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import StudyWorkspace from './StudyWorkspace'
import CodingWorkspace from './CodingWorkspace'
import LearningWorkspace from './LearningWorkspace'
import PersonalWorkspace from './PersonalWorkspace'

const COMPONENTS = {
  study: StudyWorkspace,
  coding: CodingWorkspace,
  learning: LearningWorkspace,
  personal: PersonalWorkspace,
}

export default function Container() {
  const active = useWorkspaceStore((s) => s.active)
  const Component = COMPONENTS[active]

  return (
    <div className="h-full">
      <AnimatePresence mode="wait">
        <motion.div
          key={active}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25, ease: 'easeInOut' }}
          className="h-full"
        >
          <Component />
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
