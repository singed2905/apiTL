package com.keylog.converter.controller;

import com.keylog.converter.model.ConversionRequest;
import com.keylog.converter.service.ConversionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/convert")
@CrossOrigin(origins = "*")
public class ConversionController {
    
    @Autowired
    private ConversionService conversionService;
    
    // Convert keylog format
    @PostMapping
    public ResponseEntity<Map<String, Object>> convertKeylog(
            @RequestBody ConversionRequest request) {
        try {
            String convertedData = conversionService.convertFormat(request);
            return ResponseEntity.ok(Map.of(
                "convertedData", convertedData,
                "format", request.getTargetFormat(),
                "success", true
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Conversion failed: " + e.getMessage(),
                "success", false
            ));
        }
    }
    
    // Get supported formats
    @GetMapping("/formats")
    public ResponseEntity<List<String>> getSupportedFormats() {
        return ResponseEntity.ok(conversionService.getSupportedFormats());
    }
    
    // Convert to JSON
    @PostMapping("/to-json")
    public ResponseEntity<Map<String, Object>> convertToJson(
            @RequestParam("sessionId") String sessionId) {
        try {
            String jsonData = conversionService.convertToJson(sessionId);
            return ResponseEntity.ok(Map.of(
                "jsonData", jsonData,
                "format", "json",
                "sessionId", sessionId
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "JSON conversion failed: " + e.getMessage()
            ));
        }
    }
    
    // Convert to CSV
    @PostMapping("/to-csv")
    public ResponseEntity<byte[]> convertToCsv(
            @RequestParam("sessionId") String sessionId) {
        try {
            byte[] csvData = conversionService.convertToCsv(sessionId);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("text/csv"));
            headers.setContentDispositionFormData("attachment", "keylogs_" + sessionId + ".csv");
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(csvData);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    // Convert to XML
    @PostMapping("/to-xml")
    public ResponseEntity<Map<String, Object>> convertToXml(
            @RequestParam("sessionId") String sessionId) {
        try {
            String xmlData = conversionService.convertToXml(sessionId);
            return ResponseEntity.ok(Map.of(
                "xmlData", xmlData,
                "format", "xml",
                "sessionId", sessionId
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "XML conversion failed: " + e.getMessage()
            ));
        }
    }
    
    // Batch conversion
    @PostMapping("/batch")
    public ResponseEntity<Map<String, Object>> batchConvert(
            @RequestBody List<ConversionRequest> requests) {
        try {
            Map<String, Object> results = conversionService.batchConvert(requests);
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Batch conversion failed: " + e.getMessage()
            ));
        }
    }
}