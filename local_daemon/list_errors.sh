#!/bin/bash

date='12-09'
grep -B1 failed * | grep $date | grep INFO
