import yfinance as yf
import datetime as dt
import pandas as pd
import scipy.stats as st
import numpy as np
# import plotly.graph_objects as go
# 1465, 2019-02-30


# Create fake portfolio (df)
# df = yf.download("SPY",dt.date(2010,1,1),dt.date.today(),progress=False)
# df["Portfolio Value"] = round(df['Adj Close']/df['Adj Close'].iloc[0]*10000,2)
# df.drop(['Open','High','Low','Close','Adj Close','Volume'],axis=1,inplace=True)


class PortfolioAnalysis:
    def __init__(self, portfolio):
        self.timeseries = portfolio
        self.start_date = self.timeseries.index[0]
        self.end_date = self.timeseries.index[-1]
        self.risk_free_rate = 4
        self.drawdown_list = self.get_drawdown_list()

    def get_time_period(self):
        return (self.end_date - self.start_date).days

    def get_inital_capital(self):
        inital_capital = self.timeseries["Portfolio Value"].iloc[0]
        return round(inital_capital,2)

    def get_ending_capital(self):
        ending_capital = self.timeseries["Portfolio Value"].iloc[-1]
        return round(ending_capital, 2)

    def get_peak_equity(self):
        return round(max(self.timeseries['Portfolio Value']),1)

    def get_trough_equity(self):
        return round(min(self.timeseries['Portfolio Value']),1)

    def get_net_profit(self):
        net_profit = self.get_ending_capital() - self.get_inital_capital()
        return net_profit

    def get_net_profit_percentage(self):
        get_net_profit_percentage = round(
            100 * (self.get_net_profit() / self.get_inital_capital()), 2
        )
        return get_net_profit_percentage

    def get_annual_return(self):
        time_period_days = (self.end_date - self.start_date).days
        one_plus_performance = 1 + (self.get_net_profit_percentage() * 0.01)
        annualised_return = round(
            100 * ((one_plus_performance ** (1 / (time_period_days / 365))) - 1), 2
        )
        return annualised_return

    def get_annual_risk(self):
        df = self.timeseries
        df["PercentageChange"] = 100 * df["Portfolio Value"].pct_change()
        annual_risk = round(df["PercentageChange"].std() * (252**0.5), 2)
        return annual_risk

    def get_sharpe_ratio(self):
        sharpe_ratio = round(
            (self.get_annual_return() - self.risk_free_rate) / self.get_annual_risk(), 2
        )
        return sharpe_ratio

    def get_annual_downside_deviation(self):
        df = self.timeseries
        df["PercentageChange"] = df["Portfolio Value"].pct_change()
        df['NegativePercentageChange'] = df['PercentageChange'].where(df['PercentageChange']<0)
        df = df.dropna(axis=0)
        annualised_downside_deviation = 100*df['NegativePercentageChange'].std() * (252**0.5)
        return round(annualised_downside_deviation,2)

    def get_sortino_ratio(self):
        sortino_ratio = round(
            (self.get_annual_return() - self.risk_free_rate)
            / self.get_annual_downside_deviation(),
            2,
        )
        return sortino_ratio

    def get_drawdown_list(self):
        #Create Drawdown Columns
        df = self.timeseries
        df['Max'] = df['Portfolio Value'].rolling(window=99999,min_periods=0).max()
        df['Drawdown'] = (df['Max']-df['Portfolio Value'])/df['Max']
        #Create Drawdown List
        drawdown_list = []
        for count, date in enumerate(df.index):
            #Get drawdown for yesterday
            if count != 0:
                last_value = round(df['Drawdown'].iloc[count-1],3)
            else:
                last_value = 0    
            #Get Drawdown for today
            value = round(df['Drawdown'].iloc[count],3)
            #Get Drawdown dates and append them to drawdown_list 
            if value != 0 and last_value == 0:
                start_date = date.date()
            if value == 0 and last_value != 0 or value != 0 and count == len(df.index)-1:
                end_date = date.date()
                drawdown_list.append([start_date,end_date])
        #Add time period held and maxmimum drawdown to each set of dates
        for count, drawdown_list_element in enumerate(drawdown_list):
            period = (drawdown_list_element[1] - drawdown_list_element[0]).days
            maximum_drawdown = round(100*df['Drawdown'].loc[drawdown_list_element[0]:drawdown_list_element[1]].max(),2)
            drawdown_list[count].extend([period,maximum_drawdown])
        return drawdown_list

    def get_maximum_drawdown(self):
        maximum_drawdown = np.max([element[3] for element in self.drawdown_list])
        return maximum_drawdown

    def get_length_of_maximum_drawdown(self):
        count = [element[3] for element in self.drawdown_list].index(self.get_maximum_drawdown())
        maximum_drawdown_period = (self.drawdown_list[count][1]-self.drawdown_list[count][0]).days
        return maximum_drawdown_period

    def get_longest_drawdown_period(self):
        longest_drawdown_period = np.max([element[2] for element in self.drawdown_list])
        return longest_drawdown_period

    def get_longest_drawdown(self):
        count = [element[2] for element in self.drawdown_list].index(self.get_longest_drawdown_period())
        longest_drawdown = self.drawdown_list[count][3]
        return longest_drawdown

    def get_average_drawdown(self):
        average_drawdown = np.round(np.mean([element[3] for element in self.drawdown_list]),2)
        return average_drawdown

    def get_average_drawdown_period(self):
        average_drawdown_period = np.round(np.mean([element[2] for element in self.drawdown_list]),0)
        return int(average_drawdown_period)

    def get_calmar_ratio(self):
        calmar_ratio = round((self.get_annual_return()-self.risk_free_rate)/self.get_maximum_drawdown(),2)
        return calmar_ratio

    def get_var95(self):
        df = self.timeseries
        Z = st.norm.ppf(0.95)
        var95 = round(-1 * Z * self.get_annual_risk() + self.get_annual_return(), 2)
        return var95

    def display_row(self, column_one, column_two):
        column_one, column_two = str(column_one), str(column_two)
        while len(column_one) != 30:
            column_one += " "
        while len(column_two) != 15:
            column_two += " "
        print(column_one, column_two)

    def show_timeseries(self):
        pd.options.display.max_rows = None
        print(self.timeseries)

    def print_statistics(self):
        self.display_row("", "Portfolio")
        print("-----------------------------------------")
        self.display_row("Overview", "")
        self.display_row("Start Date", self.start_date.date())
        self.display_row("End Date", self.end_date.date())
        self.display_row("Time Period", f'{self.get_time_period()} Days')
        self.display_row("Initial Capital", f"${self.get_inital_capital()}")
        self.display_row("Peak Equity", f"${self.get_peak_equity()}")
        self.display_row("Trough Equity", f"${self.get_trough_equity()}")
        self.display_row("Ending Capital", f"${self.get_ending_capital()}")
        self.display_row("Net Profits", f"${self.get_net_profit()}")
        self.display_row("Net Profits%", f"{self.get_net_profit_percentage()}%")
        self.display_row("Annual Returns", f"{self.get_annual_return()}%")
        print("-----------------------------------------")
        self.display_row("Risk", "")
        self.display_row("Annual Risk", f"{self.get_annual_risk()}%")
        self.display_row("Downside Deviation", f"{self.get_annual_downside_deviation()}%")
        self.display_row("Var(95)", f"{self.get_var95()}%")
        print("-----------------------------------------")
        self.display_row("Risk Adjusted Return", "")
        self.display_row("Sharpe Ratio", self.get_sharpe_ratio())
        self.display_row("Sortino Ratio", self.get_sortino_ratio())
        self.display_row("Calmar Ratio", self.get_calmar_ratio())
        print("-----------------------------------------")
        self.display_row("Drawdown Analysis", "")
        self.display_row("Max Drawdown", f'{self.get_maximum_drawdown()}%')
        self.display_row("Max Drawdown Period", f'{self.get_length_of_maximum_drawdown()} Days')
        self.display_row("Longest Drawdown", f'{self.get_longest_drawdown()}%')
        self.display_row("Longest Drawdown Period", f'{self.get_longest_drawdown_period()} Days')
        self.display_row("Average Drawdown", f'{self.get_average_drawdown()}%')
        self.display_row("Average Drawdown Period", f'{self.get_average_drawdown_period()} Days')
        print("-----------------------------------------")


    def show_equity_graph(self):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self.timeseries.index,
                y=self.timeseries["Portfolio Value"],
                mode="lines",
            )
        )
        fig.update_layout(
            title="Portfolio Performance",
            xaxis_title="Date",
            yaxis_title="Value in ($)",
            plot_bgcolor="white",
            title_font=dict(size=30),
            title_x=0.04,
        )
        fig.update_xaxes(linecolor="black")
        fig.update_yaxes(linecolor="black")
        fig.show()


# analysis = PortfolioAnalysis(df)
# analysis.show_timeseries()
# analysis.show_metrics()
# analysis.show_equity_graph()
