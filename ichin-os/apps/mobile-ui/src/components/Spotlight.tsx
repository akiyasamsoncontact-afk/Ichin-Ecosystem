import { useState, useEffect, useRef } from 'react'
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Modal, Keyboard } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useWorkspaceStore } from '../stores/workspaceStore'
import type { WorkspaceType } from '../types'

interface Suggestion {
  type: 'command' | 'search' | 'ai' | 'action'
  label: string
  description: string
}

const CONTEXTUAL_ACTIONS: Record<WorkspaceType, Suggestion[]> = {
  study: [
    { type: 'command', label: 'Generate Flashcards', description: 'AI creates flashcards from your notes' },
    { type: 'ai', label: 'Quiz me on current topic', description: 'Start an AI-generated quiz' },
    { type: 'action', label: 'Summarize notes', description: 'Get AI summary of recent study material' },
  ],
  coding: [
    { type: 'command', label: 'Explain this code', description: 'AI explains the selected code' },
    { type: 'ai', label: 'Find bugs', description: 'Scan for potential issues' },
    { type: 'action', label: 'Generate tests', description: 'Auto-create unit tests' },
  ],
  learning: [
    { type: 'command', label: 'Continue learning path', description: 'Resume your course progression' },
    { type: 'ai', label: 'Explain concept', description: 'Get simplified explanation' },
    { type: 'search', label: 'Find resources', description: 'Search knowledge base' },
  ],
  personal: [
    { type: 'command', label: 'Add task', description: 'Create a new task' },
    { type: 'action', label: 'Plan my day', description: 'AI organizes your schedule' },
    { type: 'search', label: 'Find notes', description: 'Search personal notes' },
  ],
}

interface Props {
  visible: boolean
  onClose: () => void
}

export default function Spotlight({ visible, onClose }: Props) {
  const insets = useSafeAreaInsets()
  const activeWs = useWorkspaceStore((s) => s.active)
  const [query, setQuery] = useState('')
  const [selectedIdx, setSelectedIdx] = useState(0)
  const inputRef = useRef<TextInput>(null)

  const allSuggestions = query
    ? CONTEXTUAL_ACTIONS[activeWs].filter((s) =>
        s.label.toLowerCase().includes(query.toLowerCase())
      )
    : CONTEXTUAL_ACTIONS[activeWs]

  useEffect(() => {
    if (visible) {
      setTimeout(() => inputRef.current?.focus(), 100)
      setSelectedIdx(0)
      setQuery('')
    }
  }, [visible])

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <TouchableOpacity activeOpacity={1} onPress={onClose} style={styles.backdrop}>
        <TouchableOpacity activeOpacity={1} style={[styles.container, { paddingTop: insets.top + 40 }]}>
          <View style={styles.inputRow}>
            <Text style={styles.searchIcon}>⌕</Text>
            <TextInput
              ref={inputRef}
              value={query}
              onChangeText={(v) => { setQuery(v); setSelectedIdx(0) }}
              placeholder="Search commands, files, or ask AI..."
              placeholderTextColor="rgba(255,255,255,0.2)"
              style={styles.input}
              returnKeyType="search"
            />
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.closeBtn}>✕</Text>
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.suggestions} keyboardShouldPersistTaps="handled">
            {allSuggestions.map((s, i) => (
              <TouchableOpacity
                key={s.label + i}
                onPress={onClose}
                style={[styles.suggestion, i === selectedIdx && styles.suggestionActive]}
              >
                <View style={styles.suggestionContent}>
                  <Text style={styles.suggestionLabel}>{s.label}</Text>
                  <Text style={styles.suggestionDesc}>{s.description}</Text>
                </View>
                <Text style={styles.suggestionType}>{s.type}</Text>
              </TouchableOpacity>
            ))}
            {allSuggestions.length === 0 && (
              <Text style={styles.empty}>No results found</Text>
            )}
          </ScrollView>
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  )
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
  },
  container: {
    flex: 1,
    paddingHorizontal: 16,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 48,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  searchIcon: {
    fontSize: 18,
    color: 'rgba(255,255,255,0.3)',
    marginRight: 8,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 15,
  },
  closeBtn: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.3)',
    padding: 4,
  },
  suggestions: {
    marginTop: 8,
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 12,
    maxHeight: 400,
  },
  suggestion: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  suggestionActive: {
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  suggestionContent: {
    flex: 1,
  },
  suggestionLabel: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
  },
  suggestionDesc: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
    marginTop: 2,
  },
  suggestionType: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.2)',
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    textTransform: 'uppercase',
  },
  empty: {
    textAlign: 'center',
    padding: 24,
    color: 'rgba(255,255,255,0.2)',
    fontSize: 13,
  },
})
