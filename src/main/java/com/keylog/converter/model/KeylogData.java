package com.keylog.converter.model;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "keylogs")
public class KeylogData {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "keystroke")
    private String keystroke;
    
    @Column(name = "timestamp")
    private LocalDateTime timestamp;
    
    @Column(name = "key_type")
    private String keyType;
    
    @Column(name = "duration")
    private Long duration;
    
    @Column(name = "session_id")
    private String sessionId;
    
    @Column(name = "key_code")
    private Integer keyCode;
    
    @Column(name = "is_modifier")
    private Boolean isModifier;
    
    // Default constructor
    public KeylogData() {}
    
    // Constructor with parameters
    public KeylogData(String keystroke, LocalDateTime timestamp, String keyType, 
                     Long duration, String sessionId) {
        this.keystroke = keystroke;
        this.timestamp = timestamp;
        this.keyType = keyType;
        this.duration = duration;
        this.sessionId = sessionId;
        this.isModifier = false;
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getKeystroke() { return keystroke; }
    public void setKeystroke(String keystroke) { this.keystroke = keystroke; }
    
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
    
    public String getKeyType() { return keyType; }
    public void setKeyType(String keyType) { this.keyType = keyType; }
    
    public Long getDuration() { return duration; }
    public void setDuration(Long duration) { this.duration = duration; }
    
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
    
    public Integer getKeyCode() { return keyCode; }
    public void setKeyCode(Integer keyCode) { this.keyCode = keyCode; }
    
    public Boolean getIsModifier() { return isModifier; }
    public void setIsModifier(Boolean isModifier) { this.isModifier = isModifier; }
    
    @Override
    public String toString() {
        return "KeylogData{" +
                "id=" + id +
                ", keystroke='" + keystroke + '\'' +
                ", timestamp=" + timestamp +
                ", keyType='" + keyType + '\'' +
                ", sessionId='" + sessionId + '\'' +
                '}';
    }
}