"""Задача В.4 — длительность реакции СКР в порах."""
import streamlit as st

from ._shared import render_precarpathian_constants


def render(cfg: dict):
    st.subheader("Задача В.4 — Длительность реакции СКР в порах")
    render_precarpathian_constants(cfg)
    st.info("В разработке.")
