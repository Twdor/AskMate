--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6

ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;

DROP TABLE IF EXISTS public.user_account;
CREATE TABLE user_account (
    id CHARACTER VARYING(255) UNIQUE NOT NULL,
    user_name CHARACTER VARYING(255) UNIQUE NOT NULL,
    email_address CHARACTER VARYING(255) UNIQUE NOT NULL,
    registration_date timestamp without time zone,
    password CHARACTER VARYING(255) UNIQUE NOT NULL,
    reputation integer
);

DROP TABLE IF EXISTS public.user_vote_status;
CREATE TABLE user_vote_status (
    id CHARACTER VARYING(255) NOT NULL,
    question_id CHARACTER VARYING(255),
    answer_id CHARACTER VARYING(255)
);

DROP TABLE IF EXISTS public.question;
CREATE TABLE question (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    view_number integer,
    vote_number integer,
    user_id CHARACTER VARYING(255) NOT NULL,
    title text,
    message text,
    image text
);

DROP TABLE IF EXISTS public.answer;
CREATE TABLE answer (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    vote_number integer,
    accepted_status BOOLEAN,
    question_id integer,
    user_id CHARACTER VARYING(255) NOT NULL,
    message text,
    image text
);

DROP TABLE IF EXISTS public.comment;
CREATE TABLE comment (
    id serial NOT NULL,
    question_id integer,
    answer_id integer,
    user_id CHARACTER VARYING(255) NOT NULL,
    message text,
    submission_time timestamp without time zone,
    edited_count integer
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);


ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);

INSERT INTO user_account VALUES ('031f03690527', 'Cabala23', 'cabala@aol.com', '2017-04-28 08:29:00', '$2b$12$K8e2Rk64VBfdjU5fiEJ7.OYTXtuAxEz516wxPM/Q4hLSbt/r3znTC', 0);
INSERT INTO user_account VALUES ('77d37d4d19a0', 'MamaMare', 'mama@gmail.com', '2018-04-28 08:29:00', '$2b$12$86ErFe/t86Y/vp9WQfJwKO7TZ0vsJNjqkGq5WPItchkiwbL2w8xJG', 0);

INSERT INTO question VALUES (0, '2017-04-28 08:29:00', 29, 0, '031f03690527', 'How to make lists in Python?', 'I am totally new to this, any hints?', NULL);
INSERT INTO question VALUES (1, '2017-04-29 09:19:00', 15, 0, '031f03690527', 'Wordpress loading multiple jQuery Versions', 'I developed a plugin that uses the jquery booklet plugin (http://builtbywill.com/booklet/#/) this plugin binds a function to $ so I cann call $(".myBook").booklet();

I could easy managing the loading order with wp_enqueue_script so first I load jquery then I load booklet so everything is fine.

BUT in my theme i also using jquery via webpack so the loading order is now following:

jquery
booklet
app.js (bundled file with webpack, including jquery)', 'images/image1.png');
INSERT INTO question VALUES (2, '2017-05-01 10:41:00', 1364, 0, '031f03690527', 'Drawing canvas with an image picked with Cordova Camera Plugin', 'I''m getting an image from device and drawing a canvas with filters using Pixi JS. It works all well using computer to get an image. But when I''m on IOS, it throws errors such as cross origin issue, or that I''m trying to use an unknown format.
', NULL);
SELECT pg_catalog.setval('question_id_seq', 2, true);

INSERT INTO answer VALUES (1, '2017-04-28 16:49:00', 0, FALSE, 1, '77d37d4d19a0', 'You need to use brackets: my_list = []', NULL);
INSERT INTO answer VALUES (2, '2017-04-25 14:42:00', 0, FALSE, 1, '77d37d4d19a0', 'Look it up in the Python docs', 'images/image2.jpg');
SELECT pg_catalog.setval('answer_id_seq', 2, true);

INSERT INTO comment VALUES (1, 0, NULL, '031f03690527', 'Please clarify the question as it is too vague!', '2017-05-01 05:49:00');
INSERT INTO comment VALUES (2, NULL, 1, '031f03690527', 'I think you could use my_list = list() as well.', '2017-05-02 16:55:00');
SELECT pg_catalog.setval('comment_id_seq', 2, true);

INSERT INTO tag VALUES (1, 'python');
INSERT INTO tag VALUES (2, 'sql');
INSERT INTO tag VALUES (3, 'css');
SELECT pg_catalog.setval('tag_id_seq', 3, true);

INSERT INTO question_tag VALUES (0, 1);
INSERT INTO question_tag VALUES (1, 3);
INSERT INTO question_tag VALUES (2, 3);
