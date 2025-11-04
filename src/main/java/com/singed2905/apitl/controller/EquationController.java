package com.singed2905.apitl.controller;

import com.singed2905.apitl.model.request.EquationRequest;
import com.singed2905.apitl.model.response.KeylogResponse;
import com.singed2905.apitl.model.response.SolutionResponse;
import com.singed2905.apitl.service.EquationService;
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
 * Equation Controller - Xử lý hệ phương trình tuyến tính
 * 
 * Hỗ trợ:
 * - Hệ 2×2, 3×3, 4×4 phương trình
 * - TL-compatible keylog encoding  
 * - Multi-version calculator support
 * - Batch processing
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/equation")
@RequiredArgsConstructor
@Tag(name = "Equation Mode", description = "Hệ phương trình tuyến tính - Linear equation systems")
public class EquationController {

    private final EquationService equationService;

    @PostMapping("/solve")
    @Operation(summary = "Giải hệ phương trình", 
               description = "Giải hệ phương trình tuyến tính 2×2, 3×3, hoặc 4×4 và tạo keylog")
    public ResponseEntity<SolutionResponse> solveEquation(
            @Valid @RequestBody EquationRequest request) {
        
        log.info("Solving equation system: {} variables, calculator: {}", 
                request.getVariables(), request.getCalculatorVersion());
        
        SolutionResponse response = equationService.solveEquation(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/keylog")
    @Operation(summary = "Tạo keylog cho hệ phương trình",
               description = "Chuyển đổi hệ phương trình thành keylog format cho máy tính Casio")
    public ResponseEntity<KeylogResponse> generateKeylog(
            @Valid @RequestBody EquationRequest request) {
        
        log.info("Generating keylog for equation: {} variables", request.getVariables());
        
        KeylogResponse response = equationService.generateKeylog(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/batch")
    @Operation(summary = "Xử lý batch nhiều hệ phương trình",
               description = "Xử lý hàng loạt nhiều hệ phương trình cùng lúc")
    public ResponseEntity<List<SolutionResponse>> solveBatch(
            @Valid @RequestBody List<EquationRequest> requests) {
        
        log.info("Processing batch of {} equation systems", requests.size());
        
        List<SolutionResponse> responses = equationService.solveBatch(requests);
        return ResponseEntity.ok(responses);
    }

    @GetMapping("/versions")
    @Operation(summary = "Danh sách phiên bản máy tính hỗ trợ",
               description = "Lấy danh sách các phiên bản máy tính Casio được hỗ trợ")
    public ResponseEntity<List<String>> getSupportedVersions() {
        List<String> versions = equationService.getSupportedCalculatorVersions();
        return ResponseEntity.ok(versions);
    }

    @GetMapping("/example/{variables}")
    @Operation(summary = "Lấy ví dụ hệ phương trình",
               description = "Lấy ví dụ hệ phương trình theo số ẩn")
    public ResponseEntity<EquationRequest> getExample(
            @Parameter(description = "Số ẩn (2, 3, hoặc 4)")
            @PathVariable int variables) {
        
        EquationRequest example = equationService.getExampleEquation(variables);
        return ResponseEntity.ok(example);
    }
}