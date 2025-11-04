package com.singed2905.apitl.service;

import com.singed2905.apitl.model.request.EquationRequest;
import com.singed2905.apitl.model.response.KeylogResponse;
import com.singed2905.apitl.model.response.SolutionResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.math3.linear.*;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * Equation Service - Xử lý hệ phương trình tuyến tính
 * 
 * Tính năng:
 * - Giải hệ 2×2, 3×3, 4×4 bằng Apache Commons Math
 * - TL-compatible keylog encoding
 * - Multi-version calculator support  
 * - Error-free workflow (luôn tạo keylog)
 * - Batch processing support
 */
@Slf4j
@Service
public class EquationService {

    /**
     * Giải hệ phương trình và tạo keylog
     */
    public SolutionResponse solveEquation(EquationRequest request) {
        long startTime = System.currentTimeMillis();
        
        try {
            log.info("Solving equation system with {} variables", request.getVariables());
            
            // Validate request
            if (!request.isValidCoefficientCount()) {
                return SolutionResponse.error("Số lượng hệ số không hợp lệ cho " + request.getVariables() + " ẩn");
            }

            // Parse coefficients
            double[][] matrix = parseCoefficientsToMatrix(request.getCoefficients(), request.getVariables());
            double[] constants = parseConstants(request.getCoefficients(), request.getVariables());

            // Solve system (với graceful error handling)
            SolutionResult result = solveSystemSafely(matrix, constants);
            
            // Generate keylog (luôn tạo dù solve fail)
            KeylogResponse keylogResponse = null;
            if (request.getGenerateKeylog()) {
                keylogResponse = generateKeylog(request);
            }

            long processingTime = System.currentTimeMillis() - startTime;

            return SolutionResponse.builder()
                    .solution(result.solutionText)
                    .solutionValues(result.solutionValues)
                    .keylogResponse(keylogResponse)
                    .variables(request.getVariables())
                    .calculatorVersion(request.getCalculatorVersion())
                    .mode("EQUATION")
                    .problemName(request.getProblemName())
                    .status("SUCCESS")
                    .processingTimeMs(processingTime)
                    .determinant(result.determinant)
                    .solutionStatus(result.status)
                    .build();

        } catch (Exception e) {
            log.error("Error solving equation: {}", e.getMessage(), e);
            return SolutionResponse.error("Lỗi khi giải hệ phương trình: " + e.getMessage());
        }
    }

    /**
     * Tạo keylog cho hệ phương trình
     */
    public KeylogResponse generateKeylog(EquationRequest request) {
        try {
            String prefix = getEquationPrefix(request.getVariables(), request.getCalculatorVersion());
            String suffix = getEquationSuffix(request.getVariables());
            
            // Encode coefficients
            String encodedCoefficients = encodeCoefficients(request.getCoefficients());
            
            // Build keylog
            String keylog = prefix + encodedCoefficients + suffix;
            
            return KeylogResponse.success(keylog, request.getCalculatorVersion(), 
                    "EQUATION", prefix, suffix);
            
        } catch (Exception e) {
            log.error("Error generating keylog: {}", e.getMessage(), e);
            return KeylogResponse.error("Lỗi tạo keylog: " + e.getMessage(), 
                    request.getCalculatorVersion(), "EQUATION");
        }
    }

    /**
     * Xử lý batch nhiều hệ phương trình
     */
    public List<SolutionResponse> solveBatch(List<EquationRequest> requests) {
        List<SolutionResponse> responses = new ArrayList<>();
        
        for (EquationRequest request : requests) {
            try {
                SolutionResponse response = solveEquation(request);
                responses.add(response);
            } catch (Exception e) {
                log.error("Error in batch processing: {}", e.getMessage(), e);
                responses.add(SolutionResponse.error("Batch error: " + e.getMessage()));
            }
        }
        
        return responses;
    }

    /**
     * Lấy danh sách calculator versions hỗ trợ
     */
    public List<String> getSupportedCalculatorVersions() {
        return Arrays.asList("fx799", "fx800", "fx801", "fx802", "fx803", "fx991", "fx570", "fx580", "fx115");
    }

    /**
     * Lấy ví dụ hệ phương trình
     */
    public EquationRequest getExampleEquation(int variables) {
        List<String> coefficients = switch (variables) {
            case 2 -> Arrays.asList("1", "2", "5", "3", "4", "11"); // x + 2y = 5, 3x + 4y = 11
            case 3 -> Arrays.asList("1", "2", "1", "6", "2", "1", "3", "14", "1", "1", "1", "6");
            case 4 -> Arrays.asList("1", "1", "1", "1", "10", "2", "1", "1", "1", "13", "1", "2", "1", "1", "11", "1", "1", "2", "1", "12");
            default -> Arrays.asList("1", "1", "2", "1", "1", "3");
        };

        return EquationRequest.builder()
                .variables(variables)
                .coefficients(coefficients)
                .calculatorVersion("fx799")
                .problemName("Ví dụ hệ " + variables + " ẩn")
                .generateKeylog(true)
                .solveSolution(true)
                .build();
    }

    // Private helper methods
    
    private double[][] parseCoefficientsToMatrix(List<String> coefficients, int variables) {
        double[][] matrix = new double[variables][variables];
        
        for (int i = 0; i < variables; i++) {
            for (int j = 0; j < variables; j++) {
                int index = i * (variables + 1) + j;
                matrix[i][j] = parseExpression(coefficients.get(index));
            }
        }
        
        return matrix;
    }
    
    private double[] parseConstants(List<String> coefficients, int variables) {
        double[] constants = new double[variables];
        
        for (int i = 0; i < variables; i++) {
            int index = i * (variables + 1) + variables; // Constant term position
            constants[i] = parseExpression(coefficients.get(index));
        }
        
        return constants;
    }
    
    private SolutionResult solveSystemSafely(double[][] matrix, double[] constants) {
        try {
            RealMatrix coefficientMatrix = new Array2DRowRealMatrix(matrix);
            RealVector constantVector = new ArrayRealVector(constants);
            
            // Check determinant
            LUDecomposition lu = new LUDecomposition(coefficientMatrix);
            double det = lu.getDeterminant();
            
            if (Math.abs(det) < 1e-10) {
                return new SolutionResult("Hệ vô nghiệm hoặc vô số nghiệm (det ≈ 0)", 
                        null, det, "NO_SOLUTION");
            }
            
            // Solve using LU decomposition
            DecompositionSolver solver = lu.getSolver();
            RealVector solution = solver.solve(constantVector);
            
            // Format solution
            StringBuilder result = new StringBuilder("Nghiệm: ");
            List<Double> values = new ArrayList<>();
            
            for (int i = 0; i < solution.getDimension(); i++) {
                double value = solution.getEntry(i);
                values.add(value);
                result.append(String.format("x%d = %.6f", i + 1, value));
                if (i < solution.getDimension() - 1) {
                    result.append(", ");
                }
            }
            
            return new SolutionResult(result.toString(), values, det, "UNIQUE_SOLUTION");
            
        } catch (Exception e) {
            log.warn("Solve failed: {}", e.getMessage());
            return new SolutionResult("Hệ vô nghiệm hoặc vô số nghiệm", null, 0.0, "ERROR");
        }
    }
    
    private double parseExpression(String expression) {
        try {
            // Basic expression parsing - can be extended
            expression = expression.trim()
                    .replace("pi", String.valueOf(Math.PI))
                    .replace("e", String.valueOf(Math.E));
            
            // Handle sqrt
            if (expression.contains("sqrt(")) {
                // Simple sqrt parsing - can be improved
                return Double.parseDouble(expression.replaceAll("sqrt\\((\\d+)\\)", "$1"));
            }
            
            return Double.parseDouble(expression);
        } catch (NumberFormatException e) {
            log.warn("Could not parse expression: {}, using 0.0", expression);
            return 0.0;
        }
    }
    
    private String encodeCoefficients(List<String> coefficients) {
        return String.join("=", coefficients);
    }
    
    private String getEquationPrefix(int variables, String calculatorVersion) {
        // TL-compatible prefixes
        return switch (variables) {
            case 2 -> "w912=";
            case 3 -> "w913=";
            case 4 -> "w914=";
            default -> "w912=";
        };
    }
    
    private String getEquationSuffix(int variables) {
        return switch (variables) {
            case 2 -> "== =";
            case 3 -> "== = =";
            case 4 -> "== = = =";
            default -> "==";
        };
    }
    
    // Helper class for solution result
    private static class SolutionResult {
        final String solutionText;
        final List<Double> solutionValues;
        final Double determinant;
        final String status;
        
        SolutionResult(String solutionText, List<Double> solutionValues, Double determinant, String status) {
            this.solutionText = solutionText;
            this.solutionValues = solutionValues;
            this.determinant = determinant;
            this.status = status;
        }
    }
}