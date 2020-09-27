from vega_datasets import data
import streamlit as st
import altair as alt
import datetime
import pandas as pd
import matplotlib.pyplot as plt
# DB
import sqlite3
conn = sqlite3.connect('Datamanagement.db')
cnn = conn.cursor()

# Functions:


def create_table():
    cnn.execute('CREATE TABLE IF NOT EXISTS data(Date DATE, Asset FLOAT, Vni FLOAT, Event TEXT)')


def add_data(Date, Asset, VnIndex, Event):
    cnn.execute('INSERT INTO Asset(Date, Asset, VnIndex, Event) VALUES (?,?,?,?)',
                (Date, Asset, VnIndex, Event))
    conn.commit()


def view_data():
    data = pd.DataFrame(pd.read_sql_query('SELECT * FROM Asset', conn))
    return data


def plotAsset(data, x_axis, y_axis):
    if x_axis != 'Date':
        Asset = pd.DataFrame(pd.read_sql_query(
            'SELECT Date, {}, {} FROM Asset'.format(x_axis, y_axis), conn))
        Asset.index = pd.to_datetime(Asset.Date)
        Asset1 = Asset[['Date', '{}'.format(x_axis)]]
        Asset1 = Asset1.pivot_table('{}'.format(x_axis), [Asset1.index.month, Asset1.index.day])
        Asset1.index = [pd.datetime(2020, month, day) for (month, day) in Asset1.index]
        st.line_chart(Asset1)
        Asset2 = Asset[['Date', '{}'.format(y_axis)]]
        Asset2 = Asset2.pivot_table('{}'.format(y_axis), [Asset2.index.month, Asset2.index.day])
        Asset2.index = [pd.datetime(2020, month, day) for (month, day) in Asset2.index]
        st.line_chart(Asset2)

    elif x_axis == 'Date':
        Asset = pd.DataFrame(pd.read_sql_query(
            "SELECT {}, {} FROM Asset".format(x_axis, y_axis), conn))
        Asset.index = pd.to_datetime(Asset.Date)
        Asset = Asset.pivot_table('{}'.format(y_axis), [Asset.index.month, Asset.index.day])
        Asset.index = [pd.datetime(2020, month, day) for (month, day) in Asset.index]
        st.line_chart(Asset)


def plotAssetvsVni():
    Asset = pd.DataFrame(pd.read_sql_query('SELECT Date, Asset, VnIndex FROM Asset', conn))
    Asset.index = pd.to_datetime(Asset.Date)
    Asset1 = Asset[['Date', 'Asset']]
    Asset1 = Asset1.pivot_table('Asset', [Asset1.index.month, Asset1.index.day])
    Asset1.index = [pd.datetime(2020, month, day) for (month, day) in Asset1.index]

    Vni = Asset[['Date', 'VnIndex']]
    Vni = Vni.pivot_table('VnIndex', [Vni.index.month, Vni.index.day])
    Vni.index = [pd.datetime(2020, month, day) for (month, day) in Vni.index]

    plt.style.use('seaborn-whitegrid')
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    Asset1.plot(ax=axes[0], linestyle='-', color='red')
    axes[0].set_title("Net Asset vs. VnIndex")
    axes[0].set_ylabel('Net Asset in Million VND')
    axes[0].legend(loc='upper left')
    Vni.plot(ax=axes[1])
    axes[1].set_ylabel('Vietnam Stock Market Index')
    axes[1].legend(loc=4)
    plt.subplots_adjust(bottom=0.15)
    st.write(fig)


def main():
    df = load_data()
    data = view_data()
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Exploration", "Data"])

    if page == "Homepage":
        st.header("This is your data explorer.")
        st.write('Stock Data')
        st.write(data)
        st.write("Please select a page on the left.")
        st.write(df)

    elif page == "Exploration":
        st.title("Data Exploration")
        x_axis = st.selectbox("Choose a variable for the x-axis", df.columns, index=3)
        y_axis = st.selectbox("Choose a variable for the y-axis", df.columns, index=4)
        visualize_data(df, x_axis, y_axis)
        st.write("Tu Anh's Net Asset")
        axis_1 = st.selectbox("Choose a variable for the x-axis", data.columns, index=1)
        axis_2 = st.selectbox("Choose a variable for the x-axis", data.columns, index=2)
        plotAsset(data, axis_1, axis_2)

    elif page == 'Data':
        st.title('Data Management')
        Date = st.date_input('Enter a Datum')
        Asset = st.number_input('Net Asset', format='%.3f')
        VnIndex = st.number_input('Vn Index', format='%.3f')
        Event = st.text_input('Enter an Event')
        if st.button("Add"):
            add_data(Date, Asset, VnIndex, Event)
            st.success("Entry is successfully inserted")


@ st.cache
def load_data():
    df = data.cars()
    return df


def visualize_data(df, x_axis, y_axis):
    graph = alt.Chart(df).mark_circle(size=60).encode(
        x=x_axis,
        y=y_axis,
        color='Origin',
        tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
    ).interactive()

    st.write(graph)


if __name__ == "__main__":
    main()
