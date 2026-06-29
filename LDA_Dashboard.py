"""
Learner Demographics and Course Enrollment Behavior Analysis on EduPro
Unified Mentor Internship Project — Data Analyst Batch Jan 2026
EduPro Online Learning Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="EduPro Learner Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Helper ───────────────────────────────────────────────────────────────────
def empty_fig(msg="No data for selected filters"):
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(size=14, color="gray"))
    fig.update_layout(height=300, template="plotly_white",
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# ─── Data Loading & Integration ──────────────────────────────────────────────
@st.cache_data
def load_data():
    users        = pd.read_csv("EduPro_Online_Platform_Users.csv")
    courses      = pd.read_csv("EduPro_Online_Platform_Courses.csv")
    transactions = pd.read_csv("EduPro_Online_Platform_Transactions.csv")

    # Force standard types
    users['UserID']   = users['UserID'].astype(str)
    users['Age']      = users['Age'].astype(int)
    users['Gender']   = users['Gender'].astype(str)

    courses['CourseID']       = courses['CourseID'].astype(str)
    courses['CourseCategory'] = courses['CourseCategory'].astype(str)
    courses['CourseType']     = courses['CourseType'].astype(str)
    courses['CourseLevel']    = courses['CourseLevel'].astype(str)

    transactions['UserID']   = transactions['UserID'].astype(str)
    transactions['CourseID'] = transactions['CourseID'].astype(str)
    transactions['TransactionDate'] = pd.to_datetime(transactions['TransactionDate'], dayfirst=True)

    # ── Data Integration: Users ↔ Transactions ↔ Courses ─────────────────────
    df = transactions.merge(
        users[['UserID', 'Age', 'Gender']], on='UserID', how='left'
    )
    df = df.merge(
        courses[['CourseID', 'CourseName', 'CourseCategory', 'CourseType', 'CourseLevel']],
        on='CourseID', how='left'
    )

    # ── Age Segmentation ──────────────────────────────────────────────────────
    df['Age_Group'] = pd.cut(
        df['Age'],
        bins=[0, 18, 25, 35, 45, 100],
        labels=['<18', '18–25', '26–35', '36–45', '45+']
    ).astype(str)

    return df, users, courses


df, users, courses = load_data()

AGE_GROUPS   = ['<18', '18–25', '26–35', '36–45', '45+']
GENDERS      = sorted(df['Gender'].unique().tolist())
CATEGORIES   = sorted(df['CourseCategory'].unique().tolist())
LEVELS       = ['Beginner', 'Intermediate', 'Advanced']

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 EduPro Analytics")
    st.markdown("**EduPro Online Learning Platform**  \nUnified Mentor · Data Analyst Intern · Jan 2026")
    st.divider()
    st.subheader("Filters")

    selected_age    = st.multiselect("Age Group",       AGE_GROUPS, default=AGE_GROUPS)
    selected_gender = st.multiselect("Gender",          GENDERS,    default=GENDERS)
    selected_cat    = st.multiselect("Course Category", CATEGORIES, default=CATEGORIES)
    selected_level  = st.multiselect("Course Level",   LEVELS,     default=LEVELS)

    st.divider()
    st.caption(f"Total users: {users.shape[0]:,} · Total courses: {courses.shape[0]:,} · Total enrollments: {len(df):,}")

# ─── Apply Filters ────────────────────────────────────────────────────────────
dff = df.copy()
if selected_age:    dff = dff[dff['Age_Group'].isin(selected_age)]
if selected_gender: dff = dff[dff['Gender'].isin(selected_gender)]
if selected_cat:    dff = dff[dff['CourseCategory'].isin(selected_cat)]
if selected_level:  dff = dff[dff['CourseLevel'].isin(selected_level)]
dff = dff.reset_index(drop=True)

# ─── KPI Calculations ────────────────────────────────────────────────────────
total_enrollments   = len(dff)
unique_learners     = dff['UserID'].nunique()
avg_courses         = round(total_enrollments / unique_learners, 2) if unique_learners > 0 else 0

# Enrollments by age group — most active age group
age_enroll     = dff['Age_Group'].value_counts()
top_age        = age_enroll.idxmax() if len(age_enroll) > 0 else 'N/A'
top_age_count  = int(age_enroll.max()) if len(age_enroll) > 0 else 0

# Gender participation ratio
male_count     = dff[dff['Gender']=='Male']['UserID'].nunique()
female_count   = dff[dff['Gender']=='Female']['UserID'].nunique()
gender_ratio   = f"M:{male_count} / F:{female_count}"

# Category popularity index — top category
cat_pop        = dff['CourseCategory'].value_counts()
top_category   = cat_pop.idxmax() if len(cat_pop) > 0 else 'N/A'

# Level preference distribution — most preferred level
level_pref     = dff['CourseLevel'].value_counts()
top_level      = level_pref.idxmax() if len(level_pref) > 0 else 'N/A'

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("# 🎓 Learner Demographics & Course Enrollment Behavior Analysis")
st.markdown("**EduPro Online Learning Platform** · 3,000 learners · 60 courses · 10,000 enrollments")
st.divider()

# ─── KPI Cards ───────────────────────────────────────────────────────────────
st.subheader("📊 KPI Summary")

if total_enrollments == 0:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filters.")
else:
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Enrollments",          f"{total_enrollments:,}",  help="Platform engagement indicator")
    with k2:
        st.metric("Enrollments by Age Group",   f"{top_age} ({top_age_count:,})", help="Most active age group")
    with k3:
        st.metric("Gender Participation Ratio", gender_ratio,              help="Inclusivity metric")
    with k4:
        st.metric("Category Popularity Index",  top_category,              help="Most enrolled course category")
    with k5:
        st.metric("Level Preference",           top_level,                 help="Most preferred course level")

    st.divider()

    # ─── Core Modules ────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Learner Demographic Overview",
        "📅 Age-wise Enrollment Charts",
        "⚧ Gender-based Course Preference",
        "📚 Course Category Popularity"
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — LEARNER DEMOGRAPHIC OVERVIEW
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("Learner Demographic Overview")

        col1, col2 = st.columns(2)

        with col1:
            # Age distribution of learners
            st.markdown("**Age distribution of learners**")
            age_dist = users['Age'].value_counts().reset_index()
            age_dist.columns = ['Age', 'Count']
            age_dist = age_dist.sort_values('Age')
            fig1 = go.Figure(go.Bar(
                x=age_dist['Age'], y=age_dist['Count'],
                marker_color='#378ADD'
            ))
            fig1.update_layout(
                height=320, template='plotly_white',
                xaxis_title='Age', yaxis_title='Number of Learners',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig1, width='content')

        with col2:
            # Gender distribution
            st.markdown("**Gender distribution across platform**")
            gender_dist = dff.groupby('Gender')['UserID'].nunique().reset_index()
            gender_dist.columns = ['Gender', 'Learners']
            fig2 = px.pie(
                gender_dist, names='Gender', values='Learners',
                color='Gender',
                color_discrete_map={'Male': '#378ADD', 'Female': '#E24B4A'}
            )
            fig2.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, width='content')

        # Participation levels per age group
        st.markdown("**Participation levels per age group — enrollment count**")
        age_part = dff[dff['Age_Group'].isin(AGE_GROUPS)]
        if len(age_part) > 0:
            age_part_ch = age_part.groupby('Age_Group').size().reindex(AGE_GROUPS).fillna(0).reset_index()
            age_part_ch.columns = ['Age Group', 'Enrollments']
            fig3 = go.Figure(go.Bar(
                x=age_part_ch['Age Group'], y=age_part_ch['Enrollments'],
                marker_color='#1D9E75'
            ))
            fig3.update_layout(
                height=300, template='plotly_white',
                xaxis_title='Age Group', yaxis_title='Total Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig3, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

        # Avg courses per learner
        st.markdown("**Average courses taken per learner by age group**")
        avg_courses_age = dff[dff['Age_Group'].isin(AGE_GROUPS)].groupby('Age_Group').apply(
            lambda x: round(len(x) / x['UserID'].nunique(), 2)
        ).reindex(AGE_GROUPS).fillna(0).reset_index()
        avg_courses_age.columns = ['Age Group', 'Avg Courses']
        if len(avg_courses_age) > 0:
            fig4 = go.Figure(go.Bar(
                x=avg_courses_age['Age Group'], y=avg_courses_age['Avg Courses'],
                marker_color='#8B5CF6'
            ))
            fig4.update_layout(
                height=300, template='plotly_white',
                xaxis_title='Age Group', yaxis_title='Avg Courses per Learner',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig4, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — AGE-WISE ENROLLMENT CHARTS
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("Age-wise Enrollment Charts")

        # Enrollments by age group
        st.markdown("**Total enrollments by age group**")
        age_enroll_ch = dff[dff['Age_Group'].isin(AGE_GROUPS)].groupby('Age_Group').size().reindex(AGE_GROUPS).fillna(0).reset_index()
        age_enroll_ch.columns = ['Age Group', 'Enrollments']
        if len(age_enroll_ch) > 0:
            fig5 = go.Figure(go.Bar(
                x=age_enroll_ch['Age Group'], y=age_enroll_ch['Enrollments'],
                marker_color='#378ADD'
            ))
            fig5.update_layout(
                height=320, template='plotly_white',
                xaxis_title='Age Group', yaxis_title='Total Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig5, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

        # Age group vs course category heatmap
        st.markdown("**Age group × course category heatmap**")
        age_cat = dff[dff['Age_Group'].isin(AGE_GROUPS)]
        if len(age_cat) > 0:
            heat = age_cat.groupby(['Age_Group', 'CourseCategory']).size().reset_index()
            heat.columns = ['Age Group', 'Course Category', 'Enrollments']
            heat_pivot = heat.pivot(index='Age Group', columns='Course Category', values='Enrollments').fillna(0)
            heat_pivot = heat_pivot.reindex([a for a in AGE_GROUPS if a in heat_pivot.index])
            fig6 = px.imshow(
                heat_pivot, text_auto=True, aspect='auto',
                color_continuous_scale='Blues',
                labels=dict(x='Course Category', y='Age Group', color='Enrollments')
            )
            fig6.update_layout(
                height=400, margin=dict(l=10, r=10, t=10, b=10)
            )
            fig6.update_xaxes(tickangle=45, tickfont=dict(size=9))
            st.plotly_chart(fig6, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

        # Age group vs course level
        st.markdown("**Age group vs course level — enrollment breakdown**")
        age_level = dff[dff['Age_Group'].isin(AGE_GROUPS) & dff['CourseLevel'].isin(LEVELS)]
        if len(age_level) > 0:
            age_level_ch = age_level.groupby(['Age_Group', 'CourseLevel']).size().reset_index()
            age_level_ch.columns = ['Age Group', 'Course Level', 'Enrollments']
            fig7 = px.bar(
                age_level_ch, x='Age Group', y='Enrollments', color='Course Level',
                barmode='group',
                color_discrete_map={'Beginner': '#1D9E75', 'Intermediate': '#EF9F27', 'Advanced': '#E24B4A'}
            )
            fig7.update_layout(
                height=360, template='plotly_white',
                yaxis_title='Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig7, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

        # Beginner vs advanced learner behavior
        st.markdown("**Beginner vs advanced learner behavior — age group distribution**")
        beg_adv = dff[dff['CourseLevel'].isin(['Beginner', 'Advanced']) & dff['Age_Group'].isin(AGE_GROUPS)]
        if len(beg_adv) > 0:
            beg_adv_ch = beg_adv.groupby(['CourseLevel', 'Age_Group']).size().reset_index()
            beg_adv_ch.columns = ['Course Level', 'Age Group', 'Enrollments']
            fig8 = px.bar(
                beg_adv_ch, x='Course Level', y='Enrollments', color='Age Group',
                barmode='group'
            )
            fig8.update_layout(
                height=340, template='plotly_white',
                yaxis_title='Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig8, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — GENDER-BASED COURSE PREFERENCE
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("Gender-based Course Preference Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Gender vs course level
            st.markdown("**Gender vs course level**")
            gen_level = dff[dff['CourseLevel'].isin(LEVELS)]
            if len(gen_level) > 0:
                gen_level_ch = gen_level.groupby(['Gender', 'CourseLevel']).size().reset_index()
                gen_level_ch.columns = ['Gender', 'Course Level', 'Enrollments']
                fig9 = px.bar(
                    gen_level_ch, x='Gender', y='Enrollments', color='Course Level',
                    barmode='group',
                    color_discrete_map={'Beginner': '#1D9E75', 'Intermediate': '#EF9F27', 'Advanced': '#E24B4A'}
                )
                fig9.update_layout(
                    height=350, template='plotly_white',
                    yaxis_title='Enrollments',
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig9, width='content')
            else:
                st.plotly_chart(empty_fig(), width='content')

        with col2:
            # Gender vs course type
            st.markdown("**Gender vs course type (Free vs Paid)**")
            gen_type = dff.groupby(['Gender', 'CourseType']).size().reset_index()
            gen_type.columns = ['Gender', 'Course Type', 'Enrollments']
            if len(gen_type) > 0:
                fig10 = px.bar(
                    gen_type, x='Gender', y='Enrollments', color='Course Type',
                    barmode='group',
                    color_discrete_map={'Free': '#1D9E75', 'Paid': '#378ADD'}
                )
                fig10.update_layout(
                    height=350, template='plotly_white',
                    yaxis_title='Enrollments',
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig10, width='content')
            else:
                st.plotly_chart(empty_fig(), width='content')

        # Gender vs course category
        st.markdown("**Gender vs course category — enrollment comparison**")
        gen_cat = dff.groupby(['Gender', 'CourseCategory']).size().reset_index()
        gen_cat.columns = ['Gender', 'Course Category', 'Enrollments']
        if len(gen_cat) > 0:
            fig11 = px.bar(
                gen_cat, x='Course Category', y='Enrollments', color='Gender',
                barmode='group',
                color_discrete_map={'Male': '#378ADD', 'Female': '#E24B4A'}
            )
            fig11.update_layout(
                height=380, template='plotly_white',
                yaxis_title='Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            fig11.update_xaxes(tickangle=45, tickfont=dict(size=9))
            st.plotly_chart(fig11, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

        # Enrollment concentration among active users by gender
        st.markdown("**Enrollment concentration — top 10 most active learners by gender**")
        top_users = dff.groupby(['UserID', 'Gender']).size().reset_index()
        top_users.columns = ['UserID', 'Gender', 'Enrollments']
        top_users = top_users.sort_values('Enrollments', ascending=False).head(10)
        if len(top_users) > 0:
            fig12 = go.Figure(go.Bar(
                x=top_users['UserID'], y=top_users['Enrollments'],
                marker_color=top_users['Gender'].map({'Male': '#378ADD', 'Female': '#E24B4A'})
            ))
            fig12.update_layout(
                height=320, template='plotly_white',
                xaxis_title='User ID', yaxis_title='Total Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig12, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — COURSE CATEGORY POPULARITY
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("Course Category Popularity Visuals")

        # Enrollments by course category
        st.markdown("**Enrollments by course category — most to least popular**")
        cat_enroll = dff['CourseCategory'].value_counts().reset_index()
        cat_enroll.columns = ['Course Category', 'Enrollments']
        if len(cat_enroll) > 0:
            fig13 = go.Figure(go.Bar(
                x=cat_enroll['Enrollments'],
                y=cat_enroll['Course Category'],
                orientation='h',
                marker_color='#378ADD'
            ))
            fig13.update_layout(
                height=420, template='plotly_white',
                xaxis_title='Total Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig13, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

        col1, col2 = st.columns(2)

        with col1:
            # Enrollments by course type
            st.markdown("**Enrollments by course type**")
            type_enroll = dff['CourseType'].value_counts().reset_index()
            type_enroll.columns = ['Course Type', 'Enrollments']
            fig14 = px.pie(
                type_enroll, names='Course Type', values='Enrollments',
                color='Course Type',
                color_discrete_map={'Free': '#1D9E75', 'Paid': '#378ADD'}
            )
            fig14.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig14, width='content')

        with col2:
            # Level preference distribution
            st.markdown("**Level preference distribution**")
            level_enroll = dff['CourseLevel'].value_counts().reindex(LEVELS).fillna(0).reset_index()
            level_enroll.columns = ['Course Level', 'Enrollments']
            fig15 = px.pie(
                level_enroll, names='Course Level', values='Enrollments',
                color='Course Level',
                color_discrete_map={'Beginner': '#1D9E75', 'Intermediate': '#EF9F27', 'Advanced': '#E24B4A'}
            )
            fig15.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig15, width='content')

        # Category × level breakdown
        st.markdown("**Course category × level breakdown**")
        cat_level = dff[dff['CourseLevel'].isin(LEVELS)].groupby(['CourseCategory', 'CourseLevel']).size().reset_index()
        cat_level.columns = ['Course Category', 'Course Level', 'Enrollments']
        if len(cat_level) > 0:
            fig16 = px.bar(
                cat_level, x='Course Category', y='Enrollments', color='Course Level',
                barmode='stack',
                color_discrete_map={'Beginner': '#1D9E75', 'Intermediate': '#EF9F27', 'Advanced': '#E24B4A'}
            )
            fig16.update_layout(
                height=400, template='plotly_white',
                yaxis_title='Enrollments',
                margin=dict(l=10, r=10, t=10, b=10)
            )
            fig16.update_xaxes(tickangle=45, tickfont=dict(size=9))
            st.plotly_chart(fig16, width='content')
        else:
            st.plotly_chart(empty_fig(), width='content')

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='font-size:12px;color:#999;text-align:center;'>"
    "Learner Demographics & Enrollment Analytics · EduPro Online Platform · "
    "Unified Mentor Internship Jan 2026 Batch · Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True
)