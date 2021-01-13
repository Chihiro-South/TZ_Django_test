insert into tb_teachers (name, positional_title, profile, avatar_url, create_time, update_time, is_delete) values
('蓝羽', 'python高级讲师', '讲师简介', '/media/c.jpg', now(), now(), 0);


insert into tb_course_category (name, create_time, update_time, is_delete) values
('python基础', now(), now(), 0),
('python高级', now(), now(), 0),
('python框架', now(), now(), 0);


insert into tb_course (title, cover_url, video_url,`profile`, outline, teacher_id, category_id, create_time, update_time, is_delete) values
('少年', 'http://kd1fxjkizfdcin9xzbe.exp.bcevod.com/mda-kd1q8dvzzifm2s0r/mda-kd1q8dvzzifm2s0r.jpg', 'http://kd1fxjkizfdcin9xzbe.exp.bcevod.com/mda-kd1q8dvzzifm2s0r/mda-kd1q8dvzzifm2s0r.m3u8','少年', '愿你们历尽千帆，归来仍是少年', 1, 2, now(), now(), 0),

('绝不会放过', 'http://kd1fxjkizfdcin9xzbe.exp.bcevod.com/mda-kd1q8mirngyk7y43/mda-kd1q8mirngyk7y43.jpg', 'http://kd1fxjkizfdcin9xzbe.exp.bcevod.com/mda-kd1q8mirngyk7y43/mda-kd1q8mirngyk7y43.m3u8', '绝不会放过', '绝不会放过', 1, 1, now(), now(), 0);
