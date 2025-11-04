package com.keylog.converter.controller;

import com.keylog.converter.model.KeylogData;
import com.keylog.converter.service.KeylogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/keylogs")
@CrossOrigin(origins = "*")
public class KeylogController {
    
    @Autowired
    private KeylogService keylogService;
    
    // Upload keylog file
    @PostMapping("/upload")
    public ResponseEntity<Map<String, String>> uploadKeylog(
            @RequestParam("file") MultipartFile file) {
        try {
            String sessionId = keylogService.processKeylogFile(file);
            return ResponseEntity.ok(Map.of(
                "message", "File uploaded successfully", 
                "sessionId", sessionId
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Failed to upload file: " + e.getMessage()
            ));
        }
    }
    
    // Get all keylogs
    @GetMapping
    public ResponseEntity<List<KeylogData>> getAllKeylogs() {
        return ResponseEntity.ok(keylogService.getAllKeylogs());
    }
    
    // Get keylogs by session
    @GetMapping("/session/{sessionId}")
    public ResponseEntity<List<KeylogData>> getKeylogsBySession(
            @PathVariable String sessionId) {
        List<KeylogData> keylogs = keylogService.getKeylogsBySession(sessionId);
        return ResponseEntity.ok(keylogs);
    }
    
    // Delete keylog data
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Boolean>> deleteKeylog(@PathVariable Long id) {
        try {
            keylogService.deleteKeylog(id);
            return ResponseEntity.ok(Map.of("deleted", true));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("deleted", false));
        }
    }
    
    // Get keylog statistics
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getOverallStats() {
        return ResponseEntity.ok(keylogService.getOverallStatistics());
    }
    
    // Search keylogs by keystroke pattern
    @GetMapping("/search")
    public ResponseEntity<List<KeylogData>> searchKeylogs(
            @RequestParam String pattern,
            @RequestParam(required = false) String sessionId) {
        List<KeylogData> results = keylogService.searchKeylogsByPattern(pattern, sessionId);
        return ResponseEntity.ok(results);
    }
}