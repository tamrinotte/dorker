# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
from re import compile as recompile

##############################

# IS DOMAIN

##############################

def is_domain(target):
    domain_pattern = recompile(
        r"^(?=.{1,253}$)(?!\-)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$"
    )
    return bool(domain_pattern.match(target.strip().lower()))