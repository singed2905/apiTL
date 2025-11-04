package com.singed2905.apitl.util;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

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
            
            if (cleaned.contains("tan(")) {
                cleaned = handleTan(cleaned);
            }
            
            if (cleaned.contains("log(")) {
                cleaned = handleLog(cleaned);
            }
            
            if (cleaned.contains("ln(")) {
                cleaned = handleLn(cleaned);
            }
            
            return Double.parseDouble(cleaned);
            
        } catch (NumberFormatException e) {
            log.warn("Could not parse expression: '{}', returning 0.0", expression);
            return 0.0;
        }
    }
    
    private static String handleSqrt(String expression) {
        try {
            Pattern pattern = Pattern.compile("sqrt\\((\\d+(?:\\.\\d+)?)\\)");
            Matcher matcher = pattern.matcher(expression);
            
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                double value = Double.parseDouble(matcher.group(1));
                double sqrtValue = Math.sqrt(value);
                matcher.appendReplacement(result, String.valueOf(sqrtValue));
            }
            matcher.appendTail(result);
            
            return result.toString();
        } catch (Exception e) {
            log.warn("Error handling sqrt in expression: {}", expression);
            return expression;
        }
    }
    
    private static String handleSin(String expression) {
        try {
            Pattern pattern = Pattern.compile("sin\\((\\d+(?:\\.\\d+)?)\\)");
            Matcher matcher = pattern.matcher(expression);
            
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                double degrees = Double.parseDouble(matcher.group(1));
                double radians = Math.toRadians(degrees);
                double sinValue = Math.sin(radians);
                matcher.appendReplacement(result, String.valueOf(sinValue));
            }
            matcher.appendTail(result);
            
            return result.toString();
        } catch (Exception e) {
            log.warn("Error handling sin in expression: {}", expression);
            return expression;
        }
    }
    
    private static String handleCos(String expression) {
        try {
            Pattern pattern = Pattern.compile("cos\\((\\d+(?:\\.\\d+)?)\\)");
            Matcher matcher = pattern.matcher(expression);
            
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                double degrees = Double.parseDouble(matcher.group(1));
                double radians = Math.toRadians(degrees);
                double cosValue = Math.cos(radians);
                matcher.appendReplacement(result, String.valueOf(cosValue));
            }
            matcher.appendTail(result);
            
            return result.toString();
        } catch (Exception e) {
            log.warn("Error handling cos in expression: {}", expression);
            return expression;
        }
    }
    
    private static String handleTan(String expression) {
        try {
            Pattern pattern = Pattern.compile("tan\\((\\d+(?:\\.\\d+)?)\\)");
            Matcher matcher = pattern.matcher(expression);
            
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                double degrees = Double.parseDouble(matcher.group(1));
                double radians = Math.toRadians(degrees);
                double tanValue = Math.tan(radians);
                matcher.appendReplacement(result, String.valueOf(tanValue));
            }
            matcher.appendTail(result);
            
            return result.toString();
        } catch (Exception e) {
            log.warn("Error handling tan in expression: {}", expression);
            return expression;
        }
    }
    
    private static String handleLog(String expression) {
        try {
            Pattern pattern = Pattern.compile("log\\((\\d+(?:\\.\\d+)?)\\)");
            Matcher matcher = pattern.matcher(expression);
            
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                double value = Double.parseDouble(matcher.group(1));
                double logValue = Math.log10(value);
                matcher.appendReplacement(result, String.valueOf(logValue));
            }
            matcher.appendTail(result);
            
            return result.toString();
        } catch (Exception e) {
            log.warn("Error handling log in expression: {}", expression);
            return expression;
        }
    }
    
    private static String handleLn(String expression) {
        try {
            Pattern pattern = Pattern.compile("ln\\((\\d+(?:\\.\\d+)?)\\)");
            Matcher matcher = pattern.matcher(expression);
            
            StringBuffer result = new StringBuffer();
            while (matcher.find()) {
                double value = Double.parseDouble(matcher.group(1));
                double lnValue = Math.log(value);
                matcher.appendReplacement(result, String.valueOf(lnValue));
            }
            matcher.appendTail(result);
            
            return result.toString();
        } catch (Exception e) {
            log.warn("Error handling ln in expression: {}", expression);
            return expression;
        }
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
    
    /**
     * Chuyển đổi degrees sang radians
     */
    public static double degreesToRadians(double degrees) {
        return Math.toRadians(degrees);
    }
    
    /**
     * Chuyển đổi radians sang degrees
     */
    public static double radiansToDegrees(double radians) {
        return Math.toDegrees(radians);
    }
    
    /**
     * Làm tròn số với số chữ số thập phân
     */
    public static double round(double value, int places) {
        if (places < 0) throw new IllegalArgumentException();
        
        long factor = (long) Math.pow(10, places);
        value = value * factor;
        long tmp = Math.round(value);
        return (double) tmp / factor;
    }
}
