import { useState } from 'react'
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native'

const FILES = [
  { name: 'src', type: 'folder' as const, children: [
    { name: 'main.ts', type: 'file' as const },
    { name: 'utils.ts', type: 'file' as const },
    { name: 'components', type: 'folder' as const, children: [
      { name: 'App.tsx', type: 'file' as const },
      { name: 'Header.tsx', type: 'file' as const },
    ]},
  ]},
  { name: 'package.json', type: 'file' as const },
  { name: 'tsconfig.json', type: 'file' as const },
]

interface FileNode {
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
}

function FileTree({ items, depth = 0 }: { items: FileNode[]; depth?: number }) {
  return (
    <View>
      {items.map((item) => (
        <View key={item.name}>
          <View style={[styles.fileItem, { paddingLeft: 12 + depth * 16 }]}>
            <Text style={[styles.fileIcon, { color: item.type === 'folder' ? 'rgba(0,230,118,0.6)' : 'rgba(255,255,255,0.4)' }]}>
              {item.type === 'folder' ? '▸' : '○'}
            </Text>
            <Text style={styles.fileName}>{item.name}</Text>
          </View>
          {item.type === 'folder' && item.children && (
            <FileTree items={item.children} depth={depth + 1} />
          )}
        </View>
      ))}
    </View>
  )
}

const WARNINGS = [
  { type: 'warning', msg: 'Unused variable: result', line: 23 },
  { type: 'error', msg: 'Type mismatch in fetchData()', line: 45 },
  { type: 'info', msg: 'Consider using const here', line: 12 },
]

const SUGGESTIONS = [
  'Add error boundary to App component',
  'Extract API calls into custom hook',
  'Add unit tests for utils module',
]

export default function CodingWorkspace() {
  const [showTerminal, setShowTerminal] = useState(false)

  return (
    <View style={styles.container}>
      <View style={styles.sidebar}>
        <Text style={styles.sectionTitle}>Explorer</Text>
        <ScrollView style={styles.fileTree}>
          <FileTree items={FILES} />
        </ScrollView>
      </View>

      <View style={styles.main}>
        <View style={styles.editorHeader}>
          <View style={styles.dots}>
            <View style={[styles.dot, { backgroundColor: '#ff5f56' }]} />
            <View style={[styles.dot, { backgroundColor: '#ffbd2e' }]} />
            <View style={[styles.dot, { backgroundColor: '#27c93f' }]} />
          </View>
          <Text style={styles.editorTitle}>main.ts</Text>
          <TouchableOpacity onPress={() => setShowTerminal(!showTerminal)}>
            <Text style={styles.terminalToggle}>$_</Text>
          </TouchableOpacity>
        </View>
        <ScrollView style={styles.codeArea}>
          <Text style={styles.code}>
            <Text style={{ color: 'rgba(0,230,118,0.6)' }}>import </Text>
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>React</Text>
            <Text style={{ color: 'rgba(0,230,118,0.6)' }}> from </Text>
            <Text style={{ color: 'rgba(255,255,255,0.4)' }}>'react'</Text>
            {'\n'}
            <Text style={{ color: 'rgba(0,230,118,0.6)' }}>import </Text>
            <Text style={{ color: 'rgba(255,255,255,0.8)' }}>{'{ useState }'}</Text>
            <Text style={{ color: 'rgba(0,230,118,0.6)' }}> from </Text>
            <Text style={{ color: 'rgba(255,255,255,0.4)' }}>'react'</Text>
            {'\n\n'}
            <Text style={{ color: 'rgba(0,230,118,0.6)' }}>function</Text>
            {' '}<Text style={{ color: 'rgba(255,255,255,0.8)' }}>App</Text>() {'{'}{'\n'}
            {'  '}<Text style={{ color: 'rgba(0,230,118,0.6)' }}>const</Text> [count, setCount] = useState(0){'\n'}
            {'  '}<Text style={{ color: 'rgba(255,255,255,0.4)' }}>// TODO: implement</Text>{'\n'}
            {'}'}
          </Text>
        </ScrollView>
        {showTerminal && (
          <View style={styles.terminal}>
            <Text style={styles.terminalText}>$ npm run dev</Text>
            <Text style={styles.terminalOutput}>VITE v6.0.0 ready in 320ms</Text>
          </View>
        )}
      </View>

      <View style={styles.panel}>
        <Text style={styles.sectionTitle}>AI Coding Agent</Text>
        <View style={styles.warningsCard}>
          <Text style={styles.cardTitle}>Warnings</Text>
          {WARNINGS.map((w, i) => (
            <View key={i} style={styles.warningItem}>
              <Text style={[styles.warningIcon, {
                color: w.type === 'error' ? '#FF5252' : w.type === 'warning' ? '#FFB300' : 'rgba(0,230,118,0.8)'
              }]}>!</Text>
              <Text style={styles.warningText}>{w.msg} L{w.line}</Text>
            </View>
          ))}
        </View>
        <View style={styles.suggestionsCard}>
          <Text style={styles.cardTitle}>Suggestions</Text>
          {SUGGESTIONS.map((s, i) => (
            <Text key={i} style={styles.suggestionItem}>→ {s}</Text>
          ))}
        </View>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: 'rgba(0, 230, 118, 0.02)',
  },
  sidebar: {
    width: 120,
    padding: 8,
  },
  sectionTitle: {
    fontSize: 10,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 6,
    paddingHorizontal: 4,
  },
  fileTree: {
    flex: 1,
  },
  fileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 4,
  },
  fileIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  fileName: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.6)',
  },
  main: {
    flex: 1,
    margin: 4,
  },
  editorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  dots: {
    flexDirection: 'row',
    gap: 4,
    marginRight: 12,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  editorTitle: {
    flex: 1,
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
  },
  terminalToggle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.3)',
  },
  codeArea: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.03)',
    padding: 12,
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
  },
  code: {
    fontFamily: 'monospace',
    fontSize: 12,
    lineHeight: 20,
  },
  terminal: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 10,
    borderRadius: 12,
    marginTop: 4,
  },
  terminalText: {
    fontFamily: 'monospace',
    fontSize: 11,
    color: 'rgba(0,230,118,0.6)',
  },
  terminalOutput: {
    fontFamily: 'monospace',
    fontSize: 11,
    color: 'rgba(255,255,255,0.4)',
  },
  panel: {
    width: 130,
    padding: 8,
  },
  warningsCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 8,
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 6,
  },
  warningItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  warningIcon: {
    fontSize: 10,
    fontWeight: 'bold',
    marginRight: 4,
    marginTop: 1,
  },
  warningText: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.5)',
    flex: 1,
  },
  suggestionsCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 8,
  },
  suggestionItem: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.4)',
    marginBottom: 4,
  },
})
