FROM ruby:latest

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN mkdir /website
WORKDIR /website

COPY Gemfile Gemfile
RUN bundle install
