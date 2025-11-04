package com.keylog.converter.service;

import com.keylog.converter.model.KeylogData;
import com.keylog.converter.repository.KeylogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class KeylogService {
    
    @Autowired
    private KeylogRepository keylogRepository;
    
    public String processKeylogFile(MultipartFile file) throws Exception {
        String sessionId = UUID.randomUUID().toString();
        
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (!line.trim().isEmpty()) {
                    KeylogData keylogData = parseKeylogLine(line, sessionId);
                    if (keylogData != null) {
                        keylogRepository.save(keylogData);
                    }
                }
            }
        }
        
        return sessionId;
    }
    
    private KeylogData parseKeylogLine(String line, String sessionId) {
        try {
            // Assuming format: timestamp,keystroke,keytype,duration
            String[] parts = line.split(",");
            if (parts.length >= 2) {
                KeylogData keylog = new KeylogData();
                keylog.setSessionId(sessionId);
                
                // Parse timestamp
                if (parts.length > 0 && !parts[0].isEmpty()) {
                    try {
                        keylog.setTimestamp(LocalDateTime.parse(parts[0], DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                    } catch (Exception e) {
                        keylog.setTimestamp(LocalDateTime.now());
                    }
                } else {
                    keylog.setTimestamp(LocalDateTime.now());
                }
                
                // Parse keystroke
                keylog.setKeystroke(parts.length > 1 ? parts[1] : "");
                
                // Parse key type
                keylog.setKeyType(parts.length > 2 ? parts[2] : "unknown");
                
                // Parse duration
                if (parts.length > 3 && !parts[3].isEmpty()) {
                    try {
                        keylog.setDuration(Long.parseLong(parts[3]));
                    } catch (NumberFormatException e) {
                        keylog.setDuration(0L);
                    }
                }
                
                // Set modifier flag
                keylog.setIsModifier(isModifierKey(keylog.getKeystroke()));
                
                return keylog;
            }
        } catch (Exception e) {
            System.err.println("Error parsing line: " + line + " - " + e.getMessage());
        }
        return null;
    }
    
    private boolean isModifierKey(String keystroke) {
        if (keystroke == null) return false;
        String key = keystroke.toLowerCase();
        return key.contains("ctrl") || key.contains("alt") || key.contains("shift") || 
               key.contains("cmd") || key.contains("meta") || key.contains("win");
    }
    
    public List<KeylogData> getAllKeylogs() {
        return keylogRepository.findAll();
    }
    
    public List<KeylogData> getKeylogsBySession(String sessionId) {
        return keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
    }
    
    public void deleteKeylog(Long id) {
        keylogRepository.deleteById(id);
    }
    
    public void deleteKeylogsBySession(String sessionId) {
        keylogRepository.deleteBySessionId(sessionId);
    }
    
    public Map<String, Object> getOverallStatistics() {
        Map<String, Object> stats = new HashMap<>();
        
        long totalKeylogs = keylogRepository.count();
        List<String> sessionIds = keylogRepository.findDistinctSessionIds();
        
        stats.put("totalKeylogs", totalKeylogs);
        stats.put("totalSessions", sessionIds.size());
        stats.put("sessionIds", sessionIds);
        
        if (totalKeylogs > 0) {
            stats.put("averageKeylogsPerSession", totalKeylogs / (double) Math.max(sessionIds.size(), 1));
        }
        
        return stats;
    }
    
    public List<KeylogData> searchKeylogsByPattern(String pattern, String sessionId) {
        if (sessionId != null && !sessionId.isEmpty()) {
            return keylogRepository.findBySessionIdAndKeystrokeContaining(sessionId, pattern);
        } else {
            return keylogRepository.findByKeystrokeContaining(pattern);
        }
    }
    
    public Map<String, Object> getSessionStatistics(String sessionId) {
        Map<String, Object> stats = new HashMap<>();
        
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        Long totalKeylogs = keylogRepository.countBySessionId(sessionId);
        
        stats.put("sessionId", sessionId);
        stats.put("totalKeylogs", totalKeylogs);
        
        if (!keylogs.isEmpty()) {
            LocalDateTime startTime = keylogs.get(0).getTimestamp();
            LocalDateTime endTime = keylogs.get(keylogs.size() - 1).getTimestamp();
            
            stats.put("startTime", startTime);
            stats.put("endTime", endTime);
            stats.put("sessionDuration", java.time.Duration.between(startTime, endTime).getSeconds());
            
            // Calculate typing speed (keys per minute)
            long durationMinutes = java.time.Duration.between(startTime, endTime).toMinutes();
            if (durationMinutes > 0) {
                stats.put("keysPerMinute", totalKeylogs / (double) durationMinutes);
            }
        }
        
        return stats;
    }
}