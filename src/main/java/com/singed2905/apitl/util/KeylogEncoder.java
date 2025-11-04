package com.singed2905.apitl.util;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * Keylog Encoder - Mã hóa keylog cho máy tính Casio
 */
@Slf4j
@Component
public class KeylogEncoder {

    /**
     * Mã hóa danh sách hệ số thành chuỗi keylog
     */
    public String encodeCoefficients(List<String> coefficients) {
        if (coefficients == null || coefficients.isEmpty()) {
            return "";
        }
        
        StringBuilder encoded = new StringBuilder();
        
        for (int i = 0; i < coefficients.size(); i++) {
            String coeff = coefficients.get(i).trim();
            
            // Basic encoding - can be extended with more complex logic
            encoded.append(encodeExpression(coeff));
            
            if (i < coefficients.size() - 1) {
                encoded.append("=");
            }
        }
        
        return encoded.toString();
    }
    
    /**
     * Mã hóa biểu thức đơn lẻ
     */
    public String encodeExpression(String expression) {
        if (expression == null || expression.trim().isEmpty()) {
            return "0";
        }
        
        String encoded = expression.trim()
                .replace("sqrt(", "\u221a(")
                .replace("pi", "\u03c0")
                .replace("infinity", "\u221e")
                .replace("*", "\u00d7")
                .replace("/", "\u00f7");
        
        log.debug("Encoded '{}' -> '{}'", expression, encoded);
        
        return encoded;
    }
    
    /**
     * Decode keylog về biểu thức gốc
     */
    public String decodeKeylog(String keylog) {
        // TODO: Implement decode logic
        return keylog;
    }
}