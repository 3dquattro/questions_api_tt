PGDMP     (                    {            tt1    15.1    15.1 
    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16815    tt1    DATABASE     w   CREATE DATABASE tt1 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE tt1;
                postgres    false            �            1259    16848 	   questions    TABLE     �   CREATE TABLE public.questions (
    id bigint NOT NULL,
    text character varying NOT NULL,
    answer character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);
    DROP TABLE public.questions;
       public         heap    postgres    false            �            1259    16847    questions_id_seq    SEQUENCE     �   ALTER TABLE public.questions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    215            �          0    16848 	   questions 
   TABLE DATA           A   COPY public.questions (id, text, answer, created_at) FROM stdin;
    public          postgres    false    215   �	       �           0    0    questions_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.questions_id_seq', 1, false);
          public          postgres    false    214            e           2606    16854    questions questions_pk 
   CONSTRAINT     T   ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pk PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.questions DROP CONSTRAINT questions_pk;
       public            postgres    false    215            g           2606    16856    questions questions_un 
   CONSTRAINT     Q   ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_un UNIQUE (text);
 @   ALTER TABLE ONLY public.questions DROP CONSTRAINT questions_un;
       public            postgres    false    215            �      x������ � �     