-- Sample data for development and testing

-- Insert sample keylog data
INSERT INTO keylogs (keystroke, timestamp, key_type, duration, session_id, key_code, is_modifier) VALUES
('h', '2025-11-04T10:00:00', 'letter', 150, 'sample-session-1', 72, false),
('e', '2025-11-04T10:00:01', 'letter', 120, 'sample-session-1', 69, false),
('l', '2025-11-04T10:00:02', 'letter', 130, 'sample-session-1', 76, false),
('l', '2025-11-04T10:00:03', 'letter', 125, 'sample-session-1', 76, false),
('o', '2025-11-04T10:00:04', 'letter', 140, 'sample-session-1', 79, false),
(' ', '2025-11-04T10:00:05', 'space', 200, 'sample-session-1', 32, false),
('w', '2025-11-04T10:00:06', 'letter', 160, 'sample-session-1', 87, false),
('o', '2025-11-04T10:00:07', 'letter', 135, 'sample-session-1', 79, false),
('r', '2025-11-04T10:00:08', 'letter', 145, 'sample-session-1', 82, false),
('l', '2025-11-04T10:00:09', 'letter', 128, 'sample-session-1', 76, false),
('d', '2025-11-04T10:00:10', 'letter', 155, 'sample-session-1', 68, false),

('t', '2025-11-04T10:05:00', 'letter', 140, 'sample-session-2', 84, false),
('e', '2025-11-04T10:05:01', 'letter', 125, 'sample-session-2', 69, false),
('s', '2025-11-04T10:05:02', 'letter', 150, 'sample-session-2', 83, false),
('t', '2025-11-04T10:05:03', 'letter', 130, 'sample-session-2', 84, false),
(' ', '2025-11-04T10:05:04', 'space', 180, 'sample-session-2', 32, false),
('d', '2025-11-04T10:05:05', 'letter', 145, 'sample-session-2', 68, false),
('a', '2025-11-04T10:05:06', 'letter', 135, 'sample-session-2', 65, false),
('t', '2025-11-04T10:05:07', 'letter', 140, 'sample-session-2', 84, false),
('a', '2025-11-04T10:05:08', 'letter', 138, 'sample-session-2', 65, false),

CTRL+('c', '2025-11-04T10:10:00', 'combination', 250, 'sample-session-3', 67, true),
CTRL+('v', '2025-11-04T10:10:02', 'combination', 220, 'sample-session-3', 86, true),
('Enter', '2025-11-04T10:10:04', 'control', 180, 'sample-session-3', 13, false),
('Backspace', '2025-11-04T10:10:06', 'control', 200, 'sample-session-3', 8, false);