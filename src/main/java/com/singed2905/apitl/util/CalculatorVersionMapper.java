package com.singed2905.apitl.util;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Calculator Version Mapper - Mapping các phiên bản máy tính
 */
@Slf4j
@Component
public class CalculatorVersionMapper {

    private final Map<String, Map<Integer, String>> equationPrefixes;
    private final Map<String, Map<Integer, String>> polynomialPrefixes;
    
    public CalculatorVersionMapper() {
        this.equationPrefixes = initEquationPrefixes();
        this.polynomialPrefixes = initPolynomialPrefixes();
    }
    
    private Map<String, Map<Integer, String>> initEquationPrefixes() {
        Map<String, Map<Integer, String>> prefixes = new HashMap<>();
        
        // fx799 - TL compatible
        Map<Integer, String> fx799 = new HashMap<>();
        fx799.put(2, "w912=");
        fx799.put(3, "w913=");
        fx799.put(4, "w914=");
        prefixes.put("fx799", fx799);
        
        // fx991
        Map<Integer, String> fx991 = new HashMap<>();
        fx991.put(2, "EQN2=");
        fx991.put(3, "EQN3=");
        fx991.put(4, "EQN4=");
        prefixes.put("fx991", fx991);
        
        return prefixes;
    }
    
    private Map<String, Map<Integer, String>> initPolynomialPrefixes() {
        Map<String, Map<Integer, String>> prefixes = new HashMap<>();
        
        // fx799
        Map<Integer, String> fx799 = new HashMap<>();
        fx799.put(2, "P2=");
        fx799.put(3, "P3=");
        fx799.put(4, "P4=");
        prefixes.put("fx799", fx799);
        
        // fx991
        Map<Integer, String> fx991 = new HashMap<>();
        fx991.put(2, "EQN2=");
        fx991.put(3, "EQN3=");
        fx991.put(4, "EQN4=");
        prefixes.put("fx991", fx991);
        
        return prefixes;
    }
    
    public String getEquationPrefix(int variables, String calculatorVersion) {
        return equationPrefixes.getOrDefault(calculatorVersion, equationPrefixes.get("fx799"))
                .getOrDefault(variables, "w912=");
    }
    
    public String getPolynomialPrefix(int degree, String calculatorVersion) {
        return polynomialPrefixes.getOrDefault(calculatorVersion, polynomialPrefixes.get("fx799"))
                .getOrDefault(degree, "P2=");
    }
    
    public List<String> getSupportedEquationVersions() {
        return Arrays.asList("fx799", "fx800", "fx801", "fx802", "fx803", "fx991");
    }
    
    public List<String> getSupportedPolynomialVersions() {
        return Arrays.asList("fx799", "fx991", "fx570", "fx580", "fx115");
    }
}