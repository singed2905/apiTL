package com.keylog.converter.model;

import java.util.Map;

public class ConversionRequest {
    private String sourceFormat;
    private String targetFormat;
    private String data;
    private String sessionId;
    private Map<String, Object> options;
    private boolean includeTimestamp;
    private boolean includeMetadata;
    
    // Default constructor
    public ConversionRequest() {}
    
    // Constructor with basic parameters
    public ConversionRequest(String sourceFormat, String targetFormat, String data) {
        this.sourceFormat = sourceFormat;
        this.targetFormat = targetFormat;
        this.data = data;
        this.includeTimestamp = true;
        this.includeMetadata = false;
    }
    
    // Getters and Setters
    public String getSourceFormat() { return sourceFormat; }
    public void setSourceFormat(String sourceFormat) { this.sourceFormat = sourceFormat; }
    
    public String getTargetFormat() { return targetFormat; }
    public void setTargetFormat(String targetFormat) { this.targetFormat = targetFormat; }
    
    public String getData() { return data; }
    public void setData(String data) { this.data = data; }
    
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
    
    public Map<String, Object> getOptions() { return options; }
    public void setOptions(Map<String, Object> options) { this.options = options; }
    
    public boolean isIncludeTimestamp() { return includeTimestamp; }
    public void setIncludeTimestamp(boolean includeTimestamp) { this.includeTimestamp = includeTimestamp; }
    
    public boolean isIncludeMetadata() { return includeMetadata; }
    public void setIncludeMetadata(boolean includeMetadata) { this.includeMetadata = includeMetadata; }
    
    @Override
    public String toString() {
        return "ConversionRequest{" +
                "sourceFormat='" + sourceFormat + '\'' +
                ", targetFormat='" + targetFormat + '\'' +
                ", sessionId='" + sessionId + '\'' +
                ", includeTimestamp=" + includeTimestamp +
                ", includeMetadata=" + includeMetadata +
                '}';
    }
}