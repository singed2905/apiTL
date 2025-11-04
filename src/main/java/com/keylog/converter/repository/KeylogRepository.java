package com.keylog.converter.repository;

import com.keylog.converter.model.KeylogData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface KeylogRepository extends JpaRepository<KeylogData, Long> {
    
    // Find keylogs by session ID
    List<KeylogData> findBySessionIdOrderByTimestampAsc(String sessionId);
    
    // Find keylogs by session ID and time range
    @Query("SELECT k FROM KeylogData k WHERE k.sessionId = :sessionId AND k.timestamp BETWEEN :startTime AND :endTime ORDER BY k.timestamp ASC")
    List<KeylogData> findBySessionIdAndTimestampBetween(
        @Param("sessionId") String sessionId,
        @Param("startTime") LocalDateTime startTime,
        @Param("endTime") LocalDateTime endTime
    );
    
    // Find keylogs by keystroke pattern
    @Query("SELECT k FROM KeylogData k WHERE k.keystroke LIKE %:pattern% ORDER BY k.timestamp ASC")
    List<KeylogData> findByKeystrokeContaining(@Param("pattern") String pattern);
    
    // Find keylogs by keystroke pattern and session
    @Query("SELECT k FROM KeylogData k WHERE k.sessionId = :sessionId AND k.keystroke LIKE %:pattern% ORDER BY k.timestamp ASC")
    List<KeylogData> findBySessionIdAndKeystrokeContaining(
        @Param("sessionId") String sessionId,
        @Param("pattern") String pattern
    );
    
    // Count total keystrokes by session
    @Query("SELECT COUNT(k) FROM KeylogData k WHERE k.sessionId = :sessionId")
    Long countBySessionId(@Param("sessionId") String sessionId);
    
    // Get distinct session IDs
    @Query("SELECT DISTINCT k.sessionId FROM KeylogData k ORDER BY k.sessionId")
    List<String> findDistinctSessionIds();
    
    // Find keylogs by key type
    List<KeylogData> findByKeyTypeAndSessionIdOrderByTimestampAsc(String keyType, String sessionId);
    
    // Get average duration by session
    @Query("SELECT AVG(k.duration) FROM KeylogData k WHERE k.sessionId = :sessionId AND k.duration IS NOT NULL")
    Double getAverageDurationBySessionId(@Param("sessionId") String sessionId);
    
    // Get keystroke frequency by session
    @Query("SELECT k.keystroke, COUNT(k) FROM KeylogData k WHERE k.sessionId = :sessionId GROUP BY k.keystroke ORDER BY COUNT(k) DESC")
    List<Object[]> getKeystrokeFrequencyBySessionId(@Param("sessionId") String sessionId);
    
    // Find modifier keys by session
    List<KeylogData> findBySessionIdAndIsModifierTrueOrderByTimestampAsc(String sessionId);
    
    // Get time range for session
    @Query("SELECT MIN(k.timestamp), MAX(k.timestamp) FROM KeylogData k WHERE k.sessionId = :sessionId")
    Object[] getTimeRangeBySessionId(@Param("sessionId") String sessionId);
    
    // Delete by session ID
    void deleteBySessionId(String sessionId);
}