package com.keylog.converter.service;

import com.keylog.converter.model.KeylogData;
import com.keylog.converter.repository.KeylogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class AnalysisService {
    
    @Autowired
    private KeylogRepository keylogRepository;
    
    public Map<String, Object> getTypingStatistics(String sessionId) {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        Map<String, Object> stats = new HashMap<>();
        
        if (keylogs.isEmpty()) {
            stats.put("error", "No data found for session: " + sessionId);
            return stats;
        }
        
        stats.put("sessionId", sessionId);
        stats.put("totalKeystrokes", keylogs.size());
        
        // Calculate time statistics
        LocalDateTime startTime = keylogs.get(0).getTimestamp();
        LocalDateTime endTime = keylogs.get(keylogs.size() - 1).getTimestamp();
        Duration sessionDuration = Duration.between(startTime, endTime);
        
        stats.put("startTime", startTime);
        stats.put("endTime", endTime);
        stats.put("sessionDurationSeconds", sessionDuration.getSeconds());
        stats.put("sessionDurationMinutes", sessionDuration.toMinutes());
        
        // Calculate typing speed
        if (sessionDuration.toMinutes() > 0) {
            double keysPerMinute = keylogs.size() / (double) sessionDuration.toMinutes();
            stats.put("keysPerMinute", Math.round(keysPerMinute * 100.0) / 100.0);
        } else {
            stats.put("keysPerMinute", 0);
        }
        
        // Count different key types
        Map<String, Long> keyTypeCounts = keylogs.stream()
            .collect(Collectors.groupingBy(
                keylog -> keylog.getKeyType() != null ? keylog.getKeyType() : "unknown",
                Collectors.counting()
            ));
        stats.put("keyTypeCounts", keyTypeCounts);
        
        // Count modifier keys
        long modifierKeys = keylogs.stream()
            .filter(keylog -> keylog.getIsModifier() != null && keylog.getIsModifier())
            .count();
        stats.put("modifierKeyCount", modifierKeys);
        
        // Calculate average duration
        OptionalDouble avgDuration = keylogs.stream()
            .filter(keylog -> keylog.getDuration() != null && keylog.getDuration() > 0)
            .mapToLong(KeylogData::getDuration)
            .average();
        
        if (avgDuration.isPresent()) {
            stats.put("averageDurationMs", Math.round(avgDuration.getAsDouble() * 100.0) / 100.0);
        } else {
            stats.put("averageDurationMs", 0);
        }
        
        return stats;
    }
    
    public Map<String, Integer> getKeyFrequency(String sessionId) {
        List<Object[]> frequencyData = keylogRepository.getKeystrokeFrequencyBySessionId(sessionId);
        Map<String, Integer> frequency = new LinkedHashMap<>();
        
        for (Object[] row : frequencyData) {
            String keystroke = (String) row[0];
            Long count = (Long) row[1];
            frequency.put(keystroke != null ? keystroke : "unknown", count.intValue());
        }
        
        return frequency;
    }
    
    public Map<String, Object> getTypingSpeedAnalysis(String sessionId) {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        Map<String, Object> speedAnalysis = new HashMap<>();
        
        if (keylogs.size() < 2) {
            speedAnalysis.put("error", "Insufficient data for speed analysis");
            return speedAnalysis;
        }
        
        List<Double> intervals = new ArrayList<>();
        List<Double> speeds = new ArrayList<>();
        
        // Calculate intervals between keystrokes
        for (int i = 1; i < keylogs.size(); i++) {
            LocalDateTime prev = keylogs.get(i-1).getTimestamp();
            LocalDateTime curr = keylogs.get(i).getTimestamp();
            
            if (prev != null && curr != null) {
                double intervalMs = Duration.between(prev, curr).toMillis();
                intervals.add(intervalMs);
                
                // Calculate instantaneous speed (keys per minute)
                if (intervalMs > 0) {
                    double speed = 60000.0 / intervalMs; // 60000 ms = 1 minute
                    speeds.add(speed);
                }
            }
        }
        
        if (!intervals.isEmpty()) {
            speedAnalysis.put("averageIntervalMs", intervals.stream().mapToDouble(Double::doubleValue).average().orElse(0));
            speedAnalysis.put("minIntervalMs", intervals.stream().mapToDouble(Double::doubleValue).min().orElse(0));
            speedAnalysis.put("maxIntervalMs", intervals.stream().mapToDouble(Double::doubleValue).max().orElse(0));
        }
        
        if (!speeds.isEmpty()) {
            speedAnalysis.put("averageSpeedKPM", speeds.stream().mapToDouble(Double::doubleValue).average().orElse(0));
            speedAnalysis.put("maxSpeedKPM", speeds.stream().mapToDouble(Double::doubleValue).max().orElse(0));
            speedAnalysis.put("minSpeedKPM", speeds.stream().mapToDouble(Double::doubleValue).min().orElse(0));
        }
        
        speedAnalysis.put("totalIntervals", intervals.size());
        return speedAnalysis;
    }
    
    public List<String> detectTypingPatterns(String sessionId) {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        List<String> patterns = new ArrayList<>();
        
        if (keylogs.size() < 3) {
            return patterns;
        }
        
        // Detect common key sequences
        Map<String, Integer> sequences = new HashMap<>();
        
        for (int i = 0; i < keylogs.size() - 2; i++) {
            String sequence = keylogs.get(i).getKeystroke() + 
                             keylogs.get(i + 1).getKeystroke() + 
                             keylogs.get(i + 2).getKeystroke();
            sequences.put(sequence, sequences.getOrDefault(sequence, 0) + 1);
        }
        
        // Find patterns that occur more than once
        sequences.entrySet().stream()
            .filter(entry -> entry.getValue() > 1)
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(10)
            .forEach(entry -> patterns.add(entry.getKey() + " (" + entry.getValue() + " times)"));
        
        // Detect typing rhythm patterns
        List<Long> intervals = new ArrayList<>();
        for (int i = 1; i < keylogs.size(); i++) {
            LocalDateTime prev = keylogs.get(i-1).getTimestamp();
            LocalDateTime curr = keylogs.get(i).getTimestamp();
            
            if (prev != null && curr != null) {
                long intervalMs = Duration.between(prev, curr).toMillis();
                intervals.add(intervalMs);
            }
        }
        
        // Analyze rhythm consistency
        if (!intervals.isEmpty()) {
            double avgInterval = intervals.stream().mapToLong(Long::longValue).average().orElse(0);
            long consistentIntervals = intervals.stream()
                .filter(interval -> Math.abs(interval - avgInterval) < avgInterval * 0.2)
                .count();
            
            double consistencyRatio = (double) consistentIntervals / intervals.size();
            if (consistencyRatio > 0.7) {
                patterns.add("Consistent typing rhythm (" + Math.round(consistencyRatio * 100) + "% consistency)");
            }
        }
        
        return patterns;
    }
    
    public Map<String, Object> getDwellTimeAnalysis(String sessionId) {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        Map<String, Object> analysis = new HashMap<>();
        
        List<Long> dwellTimes = keylogs.stream()
            .filter(keylog -> keylog.getDuration() != null && keylog.getDuration() > 0)
            .map(KeylogData::getDuration)
            .collect(Collectors.toList());
        
        if (dwellTimes.isEmpty()) {
            analysis.put("error", "No dwell time data available");
            return analysis;
        }
        
        analysis.put("averageDwellTimeMs", dwellTimes.stream().mapToLong(Long::longValue).average().orElse(0));
        analysis.put("minDwellTimeMs", dwellTimes.stream().mapToLong(Long::longValue).min().orElse(0));
        analysis.put("maxDwellTimeMs", dwellTimes.stream().mapToLong(Long::longValue).max().orElse(0));
        analysis.put("totalKeysWithDwellTime", dwellTimes.size());
        
        // Calculate standard deviation
        double mean = dwellTimes.stream().mapToLong(Long::longValue).average().orElse(0);
        double variance = dwellTimes.stream()
            .mapToDouble(time -> Math.pow(time - mean, 2))
            .average().orElse(0);
        analysis.put("dwellTimeStdDev", Math.sqrt(variance));
        
        return analysis;
    }
    
    public Map<String, Object> getFlightTimeAnalysis(String sessionId) {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        Map<String, Object> analysis = new HashMap<>();
        
        if (keylogs.size() < 2) {
            analysis.put("error", "Insufficient data for flight time analysis");
            return analysis;
        }
        
        List<Long> flightTimes = new ArrayList<>();
        
        for (int i = 1; i < keylogs.size(); i++) {
            LocalDateTime prev = keylogs.get(i-1).getTimestamp();
            LocalDateTime curr = keylogs.get(i).getTimestamp();
            
            if (prev != null && curr != null) {
                long flightTimeMs = Duration.between(prev, curr).toMillis();
                flightTimes.add(flightTimeMs);
            }
        }
        
        if (flightTimes.isEmpty()) {
            analysis.put("error", "No flight time data available");
            return analysis;
        }
        
        analysis.put("averageFlightTimeMs", flightTimes.stream().mapToLong(Long::longValue).average().orElse(0));
        analysis.put("minFlightTimeMs", flightTimes.stream().mapToLong(Long::longValue).min().orElse(0));
        analysis.put("maxFlightTimeMs", flightTimes.stream().mapToLong(Long::longValue).max().orElse(0));
        analysis.put("totalFlightTimes", flightTimes.size());
        
        // Calculate standard deviation
        double mean = flightTimes.stream().mapToLong(Long::longValue).average().orElse(0);
        double variance = flightTimes.stream()
            .mapToDouble(time -> Math.pow(time - mean, 2))
            .average().orElse(0);
        analysis.put("flightTimeStdDev", Math.sqrt(variance));
        
        return analysis;
    }
    
    public Map<String, Object> compareTypingPatterns(String sessionId1, String sessionId2) {
        Map<String, Object> comparison = new HashMap<>();
        
        Map<String, Object> stats1 = getTypingStatistics(sessionId1);
        Map<String, Object> stats2 = getTypingStatistics(sessionId2);
        
        comparison.put("session1", sessionId1);
        comparison.put("session2", sessionId2);
        comparison.put("session1Stats", stats1);
        comparison.put("session2Stats", stats2);
        
        // Compare key frequencies
        Map<String, Integer> freq1 = getKeyFrequency(sessionId1);
        Map<String, Integer> freq2 = getKeyFrequency(sessionId2);
        
        // Calculate similarity score based on common keys
        Set<String> commonKeys = new HashSet<>(freq1.keySet());
        commonKeys.retainAll(freq2.keySet());
        
        double similarityScore = (double) commonKeys.size() / 
            Math.max(freq1.keySet().size(), freq2.keySet().size());
        
        comparison.put("commonKeysCount", commonKeys.size());
        comparison.put("similarityScore", Math.round(similarityScore * 10000.0) / 100.0); // Percentage
        
        // Compare typing speeds
        Object speed1 = stats1.get("keysPerMinute");
        Object speed2 = stats2.get("keysPerMinute");
        
        if (speed1 instanceof Number && speed2 instanceof Number) {
            double speedDiff = ((Number) speed1).doubleValue() - ((Number) speed2).doubleValue();
            comparison.put("speedDifferenceKPM", Math.round(speedDiff * 100.0) / 100.0);
        }
        
        return comparison;
    }
}