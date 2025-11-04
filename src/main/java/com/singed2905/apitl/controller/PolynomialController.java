package com.singed2905.apitl.controller;

import com.singed2905.apitl.model.request.PolynomialRequest;
import com.singed2905.apitl.model.response.KeylogResponse;
import com.singed2905.apitl.model.response.SolutionResponse;
import com.singed2905.apitl.service.PolynomialService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Polynomial Controller - Xử lý phương trình đa thức
 * 
 * Hỗ trợ:
 * - Polynomial bậc 2, 3, 4
 * - Multi-version prefix system (8+ calculator versions)
 * - Complex roots handling
 * - NumPy roots engine + analytical fallback
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/polynomial")
@RequiredArgsConstructor
@Tag(name = "Polynomial Mode", description = "Phương trình đa thức - Polynomial equations")
public class PolynomialController {

    private final PolynomialService polynomialService;

    @PostMapping("/solve")
    @Operation(summary = "Giải phương trình polynomial", 
               description = "Giải phương trình polynomial bậc 2, 3, hoặc 4 với complex roots support")
    public ResponseEntity<SolutionResponse> solvePolynomial(
            @Valid @RequestBody PolynomialRequest request) {
        
        log.info("Solving polynomial degree: {}, calculator: {}", 
                request.getDegree(), request.getCalculatorVersion());
        
        SolutionResponse response = polynomialService.solvePolynomial(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/keylog")
    @Operation(summary = "Tạo keylog cho polynomial",
               description = "Chuyển đổi polynomial thành keylog với multi-version prefix support")
    public ResponseEntity<KeylogResponse> generateKeylog(
            @Valid @RequestBody PolynomialRequest request) {
        
        log.info("Generating keylog for polynomial degree: {}", request.getDegree());
        
        KeylogResponse response = polynomialService.generateKeylog(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/batch")
    @Operation(summary = "Xử lý batch nhiều polynomial",
               description = "Xử lý hàng loạt nhiều phương trình polynomial cùng lúc")
    public ResponseEntity<List<SolutionResponse>> solveBatch(
            @Valid @RequestBody List<PolynomialRequest> requests) {
        
        log.info("Processing batch of {} polynomial equations", requests.size());
        
        List<SolutionResponse> responses = polynomialService.solveBatch(requests);
        return ResponseEntity.ok(responses);
    }

    @GetMapping("/versions")
    @Operation(summary = "Danh sách phiên bản máy tính hỗ trợ",
               description = "Lấy danh sách 8+ phiên bản máy tính với prefix khác nhau")
    public ResponseEntity<List<String>> getSupportedVersions() {
        List<String> versions = polynomialService.getSupportedCalculatorVersions();
        return ResponseEntity.ok(versions);
    }

    @GetMapping("/prefixes/{version}")
    @Operation(summary = "Lấy prefixes theo version",
               description = "Lấy prefix patterns cho từng phiên bản máy tính")
    public ResponseEntity<Object> getPrefixes(
            @Parameter(description = "Calculator version (fx799, fx991, fx570, etc.)")
            @PathVariable String version) {
        
        Object prefixes = polynomialService.getPrefixesForVersion(version);
        return ResponseEntity.ok(prefixes);
    }

    @GetMapping("/example/{degree}")
    @Operation(summary = "Lấy ví dụ polynomial",
               description = "Lấy ví dụ polynomial theo bậc")
    public ResponseEntity<PolynomialRequest> getExample(
            @Parameter(description = "Bậc polynomial (2, 3, 4)")
            @PathVariable int degree) {
        
        PolynomialRequest example = polynomialService.getExamplePolynomial(degree);
        return ResponseEntity.ok(example);
    }
}