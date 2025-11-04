package com.keylog.converter.controller;

import com.keylog.converter.service.AnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/analysis")
@CrossOrigin(origins = "*")
public class AnalysisController {
    
    @Autowired
    private AnalysisService analysisService;
    
    // Get typing statistics
    @GetMapping("/stats/{sessionId}")
    public ResponseEntity<Map<String, Object>> getTypingStats(
            @PathVariable String sessionId) {
        try {
            Map<String, Object> stats = analysisService.getTypingStatistics(sessionId);
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Failed to get statistics: " + e.getMessage()
            ));
        }
    }
    
    // Get key frequency analysis
    @GetMapping("/frequency/{sessionId}")
    public ResponseEntity<Map<String, Integer>> getKeyFrequency(
            @PathVariable String sessionId) {
        try {
            Map<String, Integer> frequency = analysisService.getKeyFrequency(sessionId);
            return ResponseEntity.ok(frequency);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    // Get typing speed analysis
    @GetMapping("/speed/{sessionId}")
    public ResponseEntity<Map<String, Object>> getTypingSpeed(
            @PathVariable String sessionId) {
        try {
            Map<String, Object> speedAnalysis = analysisService.getTypingSpeedAnalysis(sessionId);
            return ResponseEntity.ok(speedAnalysis);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Failed to analyze typing speed: " + e.getMessage()
            ));
        }
    }
    
    // Get pattern analysis
    @GetMapping("/patterns/{sessionId}")
    public ResponseEntity<List<String>> getTypingPatterns(
            @PathVariable String sessionId) {
        try {
            List<String> patterns = analysisService.detectTypingPatterns(sessionId);
            return ResponseEntity.ok(patterns);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    // Get dwell time analysis
    @GetMapping("/dwell-time/{sessionId}")
    public ResponseEntity<Map<String, Object>> getDwellTimeAnalysis(
            @PathVariable String sessionId) {
        try {
            Map<String, Object> dwellTime = analysisService.getDwellTimeAnalysis(sessionId);
            return ResponseEntity.ok(dwellTime);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Failed to analyze dwell time: " + e.getMessage()
            ));
        }
    }
    
    // Get flight time analysis
    @GetMapping("/flight-time/{sessionId}")
    public ResponseEntity<Map<String, Object>> getFlightTimeAnalysis(
            @PathVariable String sessionId) {
        try {
            Map<String, Object> flightTime = analysisService.getFlightTimeAnalysis(sessionId);
            return ResponseEntity.ok(flightTime);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Failed to analyze flight time: " + e.getMessage()
            ));
        }
    }
    
    // Compare typing patterns between sessions
    @GetMapping("/compare")
    public ResponseEntity<Map<String, Object>> compareTypingPatterns(
            @RequestParam String sessionId1,
            @RequestParam String sessionId2) {
        try {
            Map<String, Object> comparison = analysisService.compareTypingPatterns(sessionId1, sessionId2);
            return ResponseEntity.ok(comparison);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Failed to compare patterns: " + e.getMessage()
            ));
        }
    }
}