import { View, Text, ScrollView, StyleSheet } from 'react-native'

const COURSES = [
  { name: 'Mathematics', progress: 100, status: 'complete' },
  { name: 'Machine Learning', progress: 65, status: 'in-progress' },
  { name: 'Deep Learning', progress: 30, status: 'in-progress' },
  { name: 'NLP', progress: 0, status: 'locked' },
]

const RESOURCES = [
  { title: 'Attention Is All You Need', type: 'Paper', source: 'arXiv' },
  { title: 'Deep Learning Book', type: 'Book', source: 'MIT Press' },
  { title: 'Transformers Course', type: 'Course', source: 'Hugging Face' },
]

export default function LearningWorkspace() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.graphCard}>
        <View style={styles.graph}>
          <View style={styles.graphCenter} />
          <View style={[styles.graphOrbit, { width: 140, height: 140 }]} />
          <View style={[styles.graphOrbit, { width: 200, height: 200 }]} />
          <View style={[styles.graphNode, { top: 30, left: 70 }]} />
          <View style={[styles.graphNode, { top: 50, right: 30 }]} />
          <View style={[styles.graphNode, { bottom: 50, left: 40 }]} />
          <View style={[styles.graphNode, { bottom: 30, right: 60 }]} />
        </View>
        <Text style={styles.graphDesc}>
          Knowledge graph visualization — showing connections between concepts in your learning path.
        </Text>
      </View>

      <View style={styles.courseCard}>
        <Text style={styles.sectionTitle}>Course Progression</Text>
        <View style={styles.courseRow}>
          {COURSES.map((c, i) => (
            <View key={c.name} style={styles.courseItem}>
              <View style={[
                styles.courseDot,
                c.status === 'complete' && { backgroundColor: 'rgba(179,136,255,0.3)' },
                c.status === 'in-progress' && { backgroundColor: 'rgba(179,136,255,0.15)' },
                c.status === 'locked' && { backgroundColor: 'rgba(255,255,255,0.05)' },
              ]}>
                <Text style={[
                  styles.courseDotText,
                  c.status === 'complete' && { color: '#B388FF' },
                  c.status === 'in-progress' && { color: '#B388FF' },
                  c.status === 'locked' && { color: 'rgba(255,255,255,0.2)' },
                ]}>
                  {c.status === 'complete' ? '✓' : c.status === 'in-progress' ? Math.floor(c.progress / 10) : '?'}
                </Text>
              </View>
              <Text style={styles.courseLabel}>{c.name}</Text>
              {i < COURSES.length - 1 && <Text style={styles.courseArrow}>→</Text>}
            </View>
          ))}
        </View>
      </View>

      <Text style={styles.sectionTitle}>Resources</Text>
      {RESOURCES.map((r, i) => (
        <View key={i} style={styles.resourceCard}>
          <Text style={styles.resourceTitle}>{r.title}</Text>
          <View style={styles.resourceMeta}>
            <Text style={styles.resourceType}>{r.type}</Text>
            <Text style={styles.resourceSource}>{r.source}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(179, 136, 255, 0.02)',
  },
  content: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
    marginTop: 8,
  },
  graphCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  graph: {
    width: 200,
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
    position: 'relative',
  },
  graphCenter: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'rgba(179,136,255,0.3)',
    position: 'absolute',
  },
  graphOrbit: {
    position: 'absolute',
    borderRadius: 100,
    borderWidth: 1,
    borderColor: 'rgba(179,136,255,0.1)',
  },
  graphNode: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#B388FF',
    position: 'absolute',
    opacity: 0.5,
  },
  graphDesc: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    textAlign: 'center',
  },
  courseCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  courseRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  courseItem: {
    alignItems: 'center',
    flex: 1,
  },
  courseDot: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  courseDotText: {
    fontSize: 12,
    fontWeight: '600',
  },
  courseLabel: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.3)',
    marginTop: 4,
    textAlign: 'center',
  },
  courseArrow: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.1)',
    marginTop: -16,
  },
  resourceCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
  },
  resourceTitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.7)',
    marginBottom: 4,
  },
  resourceMeta: {
    flexDirection: 'row',
    gap: 8,
  },
  resourceType: {
    fontSize: 10,
    color: '#B388FF',
    backgroundColor: 'rgba(179,136,255,0.1)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  resourceSource: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.2)',
  },
})
