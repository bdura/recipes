FROM ruby:latest

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN mkdir /website
WORKDIR /website

RUN gem install i18n
RUN gem install latex-decode

COPY Gemfile Gemfile
RUN bundle install
RUN bundle add i18n
RUN bundle add latex-decode
