package com.singed2905.apitl.util;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * Math Utils - Tiện ích toán học
 */
@Slf4j
@Component
public class MathUtils {

    /**
     * Parse biểu thức toán học thành số
     */
    public static double parseExpression(String expression) {
        try {
            if (expression == null || expression.trim().isEmpty()) {
                return 0.0;
            }
            
            String cleaned = expression.trim()
                    .replace("pi", String.valueOf(Math.PI))
                    .replace("e", String.valueOf(Math.E))
                    .replace("\u03c0", String.valueOf(Math.PI));
            
            // Handle basic functions
            if (cleaned.contains("sqrt(")) {
                cleaned = handleSqrt(cleaned);
            }
            
            if (cleaned.contains("sin(")) {
                cleaned = handleSin(cleaned);
            }
            
            if (cleaned.contains("cos(")) {
                cleaned = handleCos(cleaned);
            }
            
            return Double.parseDouble(cleaned);
            
        } catch (NumberFormatException e) {
            log.warn("Could not parse expression: '{}', returning 0.0", expression);
            return 0.0;
        }
    }
    
    private static String handleSqrt(String expression) {
        // Simple sqrt parsing - can be improved with proper expression parser
        return expression.replaceAll("sqrt\\((\\d+(?:\\.\\d+)?)\\)", 
                match -> String.valueOf(Math.sqrt(Double.parseDouble(match.replaceAll("sqrt\\(|\\)", "")))));
    }
    
    private static String handleSin(String expression) {
        return expression.replaceAll("sin\\((\\d+(?:\\.\\d+)?)\\)", 
                match -> String.valueOf(Math.sin(Double.parseDouble(match.replaceAll("sin\\(|\\)", "")))));
    }
    
    private static String handleCos(String expression) {
        return expression.replaceAll("cos\\((\\d+(?:\\.\\d+)?)\\)", 
                match -> String.valueOf(Math.cos(Double.parseDouble(match.replaceAll("cos\\(|\\)", "")))));
    }
    
    /**
     * Format số với độ chính xác cho trước
     */
    public static String formatNumber(double number, int precision) {
        return String.format("%."+precision+"f", number);
    }
    
    /**
     * Kiểm tra số phức
     */
    public static boolean isComplexNumber(String expression) {
        return expression != null && (expression.contains("i") || expression.contains("j"));
    }
}