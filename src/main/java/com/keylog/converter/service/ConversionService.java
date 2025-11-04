package com.keylog.converter.service;

import com.keylog.converter.model.ConversionRequest;
import com.keylog.converter.model.KeylogData;
import com.keylog.converter.repository.KeylogRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.StringWriter;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class ConversionService {
    
    @Autowired
    private KeylogRepository keylogRepository;
    
    private final ObjectMapper objectMapper;
    
    public ConversionService() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
    }
    
    public String convertFormat(ConversionRequest request) throws Exception {
        switch (request.getTargetFormat().toLowerCase()) {
            case "json":
                return convertToJsonFormat(request);
            case "csv":
                return convertToCsvFormat(request);
            case "xml":
                return convertToXmlFormat(request);
            case "txt":
                return convertToTextFormat(request);
            default:
                throw new UnsupportedOperationException("Format not supported: " + request.getTargetFormat());
        }
    }
    
    public List<String> getSupportedFormats() {
        return Arrays.asList("json", "csv", "xml", "txt");
    }
    
    public String convertToJson(String sessionId) throws Exception {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        Map<String, Object> result = new HashMap<>();
        result.put("sessionId", sessionId);
        result.put("totalKeylogs", keylogs.size());
        result.put("keylogs", keylogs);
        
        return objectMapper.writeValueAsString(result);
    }
    
    public byte[] convertToCsv(String sessionId) throws Exception {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        
        StringBuilder csv = new StringBuilder();
        csv.append("ID,Keystroke,Timestamp,KeyType,Duration,SessionId,KeyCode,IsModifier\n");
        
        for (KeylogData keylog : keylogs) {
            csv.append(keylog.getId()).append(",")
               .append(escapeCSV(keylog.getKeystroke())).append(",")
               .append(keylog.getTimestamp() != null ? keylog.getTimestamp().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : "").append(",")
               .append(escapeCSV(keylog.getKeyType())).append(",")
               .append(keylog.getDuration() != null ? keylog.getDuration() : "").append(",")
               .append(escapeCSV(keylog.getSessionId())).append(",")
               .append(keylog.getKeyCode() != null ? keylog.getKeyCode() : "").append(",")
               .append(keylog.getIsModifier() != null ? keylog.getIsModifier() : "false")
               .append("\n");
        }
        
        return csv.toString().getBytes();
    }
    
    public String convertToXml(String sessionId) throws Exception {
        List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(sessionId);
        
        StringBuilder xml = new StringBuilder();
        xml.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        xml.append("<keylogs sessionId=\"").append(sessionId).append("\">\n");
        
        for (KeylogData keylog : keylogs) {
            xml.append("  <keylog>\n");
            xml.append("    <id>").append(keylog.getId()).append("</id>\n");
            xml.append("    <keystroke>").append(escapeXml(keylog.getKeystroke())).append("</keystroke>\n");
            xml.append("    <timestamp>").append(keylog.getTimestamp() != null ? keylog.getTimestamp().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : "").append("</timestamp>\n");
            xml.append("    <keyType>").append(escapeXml(keylog.getKeyType())).append("</keyType>\n");
            xml.append("    <duration>").append(keylog.getDuration() != null ? keylog.getDuration() : "").append("</duration>\n");
            xml.append("    <sessionId>").append(escapeXml(keylog.getSessionId())).append("</sessionId>\n");
            xml.append("    <keyCode>").append(keylog.getKeyCode() != null ? keylog.getKeyCode() : "").append("</keyCode>\n");
            xml.append("    <isModifier>").append(keylog.getIsModifier() != null ? keylog.getIsModifier() : "false").append("</isModifier>\n");
            xml.append("  </keylog>\n");
        }
        
        xml.append("</keylogs>\n");
        return xml.toString();
    }
    
    private String convertToJsonFormat(ConversionRequest request) throws Exception {
        if (request.getSessionId() != null) {
            return convertToJson(request.getSessionId());
        } else {
            // Convert raw data
            Map<String, Object> result = new HashMap<>();
            result.put("data", request.getData());
            result.put("format", "json");
            return objectMapper.writeValueAsString(result);
        }
    }
    
    private String convertToCsvFormat(ConversionRequest request) throws Exception {
        if (request.getSessionId() != null) {
            return new String(convertToCsv(request.getSessionId()));
        } else {
            // Simple CSV conversion from raw data
            return "data\n" + escapeCSV(request.getData()) + "\n";
        }
    }
    
    private String convertToXmlFormat(ConversionRequest request) throws Exception {
        if (request.getSessionId() != null) {
            return convertToXml(request.getSessionId());
        } else {
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<data>" + escapeXml(request.getData()) + "</data>";
        }
    }
    
    private String convertToTextFormat(ConversionRequest request) throws Exception {
        if (request.getSessionId() != null) {
            List<KeylogData> keylogs = keylogRepository.findBySessionIdOrderByTimestampAsc(request.getSessionId());
            StringBuilder text = new StringBuilder();
            text.append("Keylog Data for Session: ").append(request.getSessionId()).append("\n");
            text.append("=" .repeat(50)).append("\n");
            
            for (KeylogData keylog : keylogs) {
                text.append("Time: ").append(keylog.getTimestamp())
                    .append(", Key: ").append(keylog.getKeystroke())
                    .append(", Type: ").append(keylog.getKeyType())
                    .append(", Duration: ").append(keylog.getDuration())
                    .append("\n");
            }
            
            return text.toString();
        } else {
            return request.getData();
        }
    }
    
    public Map<String, Object> batchConvert(List<ConversionRequest> requests) throws Exception {
        Map<String, Object> results = new HashMap<>();
        List<Map<String, Object>> conversions = new ArrayList<>();
        
        for (int i = 0; i < requests.size(); i++) {
            ConversionRequest request = requests.get(i);
            Map<String, Object> conversion = new HashMap<>();
            
            try {
                String converted = convertFormat(request);
                conversion.put("index", i);
                conversion.put("success", true);
                conversion.put("data", converted);
                conversion.put("format", request.getTargetFormat());
            } catch (Exception e) {
                conversion.put("index", i);
                conversion.put("success", false);
                conversion.put("error", e.getMessage());
            }
            
            conversions.add(conversion);
        }
        
        results.put("totalRequests", requests.size());
        results.put("conversions", conversions);
        results.put("timestamp", new Date());
        
        return results;
    }
    
    private String escapeCSV(String value) {
        if (value == null) return "";
        if (value.contains(",") || value.contains("\"") || value.contains("\n")) {
            return "\"" + value.replace("\"", "\\\"") + "\"";
        }
        return value;
    }
    
    private String escapeXml(String value) {
        if (value == null) return "";
        return value.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace("\"", "&quot;")
                   .replace("'", "&apos;");
    }
}