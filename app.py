import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de salários na área de dados",
    page_icon=":bar_chart:",
    layout="wide",
)

df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

available_years = sorted(df['ano'].unique())
selected_years = st.sidebar.multiselect("Year", available_years, default=available_years)

available_levels = sorted(df['senioridade'].unique())
selected_levels = st.sidebar.multiselect("Level", available_levels, default=available_levels)

available_contracts = sorted(df['contrato'].unique())
selected_contracts = st.sidebar.multiselect("Contract", available_contracts, default=available_contracts)

available_size_company = sorted(df['tamanho_empresa'].unique())
selected_size_company = st.sidebar.multiselect("Company Size", available_size_company, default=available_size_company)

# --- Filtragem do DataFrame ---
filtered_df = df[
    (df['ano'].isin(selected_years)) &
    (df['senioridade'].isin(selected_levels)) &
    (df['contrato'].isin(selected_contracts)) &
    (df['tamanho_empresa'].isin(selected_size_company))
]

st.title("Dashboard de análise de salários na área de dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos.")

st.subheader("Métricas gerais (Salário anual em USD)")

if not filtered_df.empty:
    half_salary = filtered_df['usd'].mean()
    max_salary = filtered_df['usd'].max()
    total_data = filtered_df.shape[0]
    most_frequent_job = filtered_df['cargo'].mode()[0]
else:
    half_salary, max_salary, total_data, most_frequent_job = 0, 0, 0, ""

half_column, max_column, total_column, most_frequent_column = st.columns(4)
half_column.metric("Salário médio", f"${half_salary:,.0f}")
max_column.metric("Maior salário", f"${max_salary:,.0f}")
total_column.metric("Total de registros", f"${total_data:,}")
most_frequent_column.metric("Cargo mais frequente", most_frequent_job)

st.markdown("---")

# --- Análises virtuais com Pyplot ---
st.subheader("Gráficos")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not filtered_df.empty:
        top_jobs = filtered_df.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        jobs_graphic = px.bar(
            top_jobs,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 cargos por salário médio',
            labels={'usd':'Média salarial anual (USD)', 'cargo': ''}
        )
        jobs_graphic.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(jobs_graphic, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado para este filtro.")

with col_graf2:
    if not filtered_df.empty:
        hist_graphic = px.histogram(
            filtered_df,
            x='usd',
            nbins=30,
            title='Distribuição de salários anuais',
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        hist_graphic.update_layout(title_x=0.1)
        st.plotly_chart(hist_graphic, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado para este filtro.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not filtered_df.empty:
        remote_count = filtered_df['remoto'].value_counts().reset_index()
        remote_count.columns = ['tipo_trabalho', 'quantidade']
        remote_graphic = px.pie(
            remote_count,
            values='quantidade',
            names='tipo_trabalho',
            title='Porcentagem dos tipos de trabalho',
            hole=0.5,
        )
        remote_graphic.update_traces(textinfo='percent+label')
        remote_graphic.update_layout(title_x=0.1)
        st.plotly_chart(remote_graphic, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado para este filtro.")

with col_graf4:
    if not filtered_df.empty:
        df_ds = filtered_df[filtered_df['cargo'] == 'Data Scientist']
        country_media = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        country_graphic = px.choropleth(
            country_media,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de dados no país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
        )
        country_graphic.update_layout(title_x=0.1)
        st.plotly_chart(country_graphic, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado para este filtro.")

# ---- Tabela de dados detalhados
st.subheader("Dados detalhados")
st.dataframe(filtered_df)