package com.singed2905.apitl.model.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Solution Response - Kết quả giải toán
 * 
 * Chứa nghiệm toán học và keylog tương ứng
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Kết quả giải toán response")
public class SolutionResponse {

    @Schema(description = "Nghiệm toán học (text format)", 
            example = "Nghiệm: x1 = 1.000000, x2 = 2.000000, x3 = 1.000000")
    private String solution;

    @Schema(description = "Danh sách nghiệm (numeric format)")
    private List<Double> solutionValues;

    @Schema(description = "Kết quả keylog nếu được yêu cầu")
    private KeylogResponse keylogResponse;

    @Schema(description = "Số ẩn hoặc bậc của phương trình", example = "3")
    private Integer variables;

    @Schema(description = "Phiên bản máy tính", example = "fx799")
    private String calculatorVersion;

    @Schema(description = "Mode toán học", 
            example = "EQUATION",
            allowableValues = {"EQUATION", "POLYNOMIAL", "GEOMETRY", "VECTOR"})
    private String mode;

    @Schema(description = "Tên bài toán", example = "Hệ phương trình bài 1")
    private String problemName;

    @Schema(description = "Thời gian xử lý")
    private LocalDateTime processedAt;

    @Schema(description = "Thời gian xử lý (milliseconds)", example = "150")
    private Long processingTimeMs;

    @Schema(description = "Trạng thái xử lý", example = "SUCCESS")
    private String status;

    @Schema(description = "Thông báo lỗi nếu có")
    private String errorMessage;

    @Schema(description = "Thông tin debug")
    private String debugInfo;

    @Schema(description = "Determinant của ma trận (cho equation mode)", example = "12.0")
    private Double determinant;

    @Schema(description = "Trạng thái nghiệm", 
            example = "UNIQUE_SOLUTION",
            allowableValues = {"UNIQUE_SOLUTION", "NO_SOLUTION", "INFINITE_SOLUTIONS", "COMPLEX_ROOTS"})
    private String solutionStatus;

    public static SolutionResponse success(String solution, String mode) {
        return SolutionResponse.builder()
                .solution(solution)
                .mode(mode)
                .processedAt(LocalDateTime.now())
                .status("SUCCESS")
                .solutionStatus("UNIQUE_SOLUTION")
                .build();
    }

    public static SolutionResponse error(String errorMessage) {
        return SolutionResponse.builder()
                .errorMessage(errorMessage)
                .processedAt(LocalDateTime.now())
                .status("ERROR")
                .build();
    }
}