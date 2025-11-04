package com.singed2905.apitl.model.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;

/**
 * Keylog Response - Kết quả keylog cho máy tính Casio
 * 
 * Chứa keylog string đã được mã hóa và thông tin metadata
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Kết quả keylog response")
public class KeylogResponse {

    @Schema(description = "Chuỗi keylog đã mã hóa", 
            example = "w913=1=2=3=4=5=6=7=8=9=10=11=12== = =")
    private String keylog;

    @Schema(description = "Phiên bản máy tính được sử dụng", example = "fx799")
    private String calculatorVersion;

    @Schema(description = "Loại mode được sử dụng", 
            example = "EQUATION", 
            allowableValues = {"EQUATION", "POLYNOMIAL", "GEOMETRY", "VECTOR"})
    private String mode;

    @Schema(description = "Prefix được sử dụng", example = "w913")
    private String prefix;

    @Schema(description = "Suffix được sử dụng", example = "== = =")
    private String suffix;

    @Schema(description = "Số ký tự trong keylog", example = "45")
    private Integer keylogLength;

    @Schema(description = "Thời gian tạo keylog")
    private LocalDateTime generatedAt;

    @Schema(description = "Trạng thái tạo keylog", example = "SUCCESS")
    private String status;

    @Schema(description = "Thông báo lỗi nếu có")
    private String errorMessage;

    @Schema(description = "Thông tin debug nếu cần")
    private String debugInfo;

    public static KeylogResponse success(String keylog, String calculatorVersion, 
                                       String mode, String prefix, String suffix) {
        return KeylogResponse.builder()
                .keylog(keylog)
                .calculatorVersion(calculatorVersion)
                .mode(mode)
                .prefix(prefix)
                .suffix(suffix)
                .keylogLength(keylog.length())
                .generatedAt(LocalDateTime.now())
                .status("SUCCESS")
                .build();
    }

    public static KeylogResponse error(String errorMessage, String calculatorVersion, String mode) {
        return KeylogResponse.builder()
                .calculatorVersion(calculatorVersion)
                .mode(mode)
                .generatedAt(LocalDateTime.now())
                .status("ERROR")
                .errorMessage(errorMessage)
                .build();
    }
}