import { useState } from 'react'
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Modal } from 'react-native'

const SECTIONS = [
  { id: 'behavior', label: 'AI Behavior' },
  { id: 'focus', label: 'Focus Mode' },
  { id: 'permissions', label: 'Agent Permissions' },
  { id: 'shortcuts', label: 'Shortcuts' },
  { id: 'privacy', label: 'Privacy Controls' },
]

const SHORTCUTS = [
  { keys: 'Ctrl + Space', action: 'Open Spotlight' },
  { keys: 'Ctrl + A', action: 'Open AI Council' },
  { keys: 'Ctrl + F', action: 'Cycle Focus Mode' },
  { keys: 'Ctrl + Tab', action: 'Cycle Workspace' },
  { keys: 'Esc', action: 'Close panel' },
]

interface Props {
  visible: boolean
  onClose: () => void
}

export default function Settings({ visible, onClose }: Props) {
  const [section, setSection] = useState('behavior')

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <TouchableOpacity activeOpacity={1} onPress={onClose} style={styles.backdrop}>
        <TouchableOpacity activeOpacity={1} style={styles.container}>
          <View style={styles.handle} />
          <View style={styles.header}>
            <Text style={styles.title}>Settings</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.closeBtn}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabsRow}>
            {SECTIONS.map((s) => (
              <TouchableOpacity
                key={s.id}
                onPress={() => setSection(s.id)}
                style={[styles.tab, section === s.id && styles.tabActive]}
              >
                <Text style={[styles.tabText, section === s.id && styles.tabTextActive]}>{s.label}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <ScrollView style={styles.content}>
            {section === 'behavior' && (
              <View style={styles.sectionContent}>
                <Text style={styles.optionLabel}>AI Aggression Level</Text>
                <View style={styles.sliderRow}>
                  <Text style={styles.sliderLabel}>Passive</Text>
                  <View style={styles.sliderTrack}>
                    <View style={[styles.sliderFill, { width: '50%' }]} />
                  </View>
                  <Text style={styles.sliderLabel}>Aggressive</Text>
                </View>
              </View>
            )}

            {section === 'focus' && (
              <View style={styles.sectionContent}>
                {['Normal', 'Focus', 'Deep Focus', 'Lock'].map((m) => (
                  <View key={m} style={styles.settingRow}>
                    <Text style={styles.settingLabel}>{m}</Text>
                    <Text style={styles.settingCheck}>✓</Text>
                  </View>
                ))}
              </View>
            )}

            {section === 'permissions' && (
              <View style={styles.sectionContent}>
                {['orion', 'nova', 'sage', 'pulse', 'echo', 'iris', 'atlas', 'aegis'].map((agent) => (
                  <View key={agent} style={styles.settingRow}>
                    <Text style={styles.settingLabel}>{agent}</Text>
                    <Text style={styles.settingCheck}>✓</Text>
                  </View>
                ))}
              </View>
            )}

            {section === 'shortcuts' && (
              <View style={styles.sectionContent}>
                {SHORTCUTS.map((s) => (
                  <View key={s.action} style={styles.settingRow}>
                    <Text style={styles.settingLabel}>{s.action}</Text>
                    <Text style={styles.shortcutKeys}>{s.keys}</Text>
                  </View>
                ))}
              </View>
            )}

            {section === 'privacy' && (
              <View style={styles.sectionContent}>
                <View style={styles.privacyCard}>
                  <Text style={styles.privacyTitle}>Memory Management</Text>
                  <Text style={styles.privacyDesc}>Total stored memories: 1,432 items</Text>
                  <TouchableOpacity style={styles.dangerBtn}>
                    <Text style={styles.dangerBtnText}>Clear Session</Text>
                  </TouchableOpacity>
                </View>
              </View>
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
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: '#0A0A0A',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '85%',
    paddingHorizontal: 16,
    paddingBottom: 30,
  },
  handle: {
    width: 36,
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 2,
    alignSelf: 'center',
    marginTop: 8,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.8)',
  },
  closeBtn: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.3)',
    padding: 4,
  },
  tabsRow: {
    marginBottom: 16,
  },
  tab: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 8,
    marginRight: 6,
    backgroundColor: 'rgba(255,255,255,0.05)',
  },
  tabActive: {
    backgroundColor: 'rgba(255,255,255,0.12)',
  },
  tabText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
  },
  tabTextActive: {
    color: 'rgba(255,255,255,0.8)',
  },
  content: {
    maxHeight: 400,
  },
  sectionContent: {
    gap: 10,
  },
  optionLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    marginBottom: 4,
  },
  sliderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  sliderLabel: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.2)',
  },
  sliderTrack: {
    flex: 1,
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 2,
  },
  sliderFill: {
    height: '100%',
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: 2,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 12,
    borderRadius: 10,
  },
  settingLabel: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.7)',
    textTransform: 'capitalize',
  },
  settingCheck: {
    fontSize: 14,
    color: 'rgba(0,230,118,0.6)',
  },
  shortcutKeys: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
    fontFamily: 'monospace',
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  privacyCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 16,
  },
  privacyTitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.5)',
    marginBottom: 4,
  },
  privacyDesc: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
    marginBottom: 12,
  },
  dangerBtn: {
    backgroundColor: 'rgba(255,82,82,0.1)',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  dangerBtnText: {
    fontSize: 11,
    color: 'rgba(255,82,82,0.6)',
  },
})
