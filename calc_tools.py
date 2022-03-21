from re import I
from typing import final
import matplotlib.pyplot as plt
import numpy as np

def generate_flat(rate, months = 60):
    return np.ones(months) * rate

def make_plots_vs_time(outputs, labels):
    list_of_plots = ['payments', 'interest_payments', 'principal_payments', 'balance']

    for plot in list_of_plots:
        plot_vs_time([x[plot] for x in outputs], labels, plot)

    plot_vs_time([x['principal_payments'] / x['payments'] for x in outputs], labels, 'Fraction of principal in payment')

def plot_vs_time(y_list, labels, ylabel = 'Balance', xlabel = 'Month', month = True):
    if month:
        x = range(0, 60, 1)
    else:
        x = range(0, 5, 1./12.)
    
    for y in y_list:
        plt.plot(x, y)
    

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(labels)

    plt.show()

def calculate_monthly_rate(annual_rate, monthly = False):
    annual_rate_dec = annual_rate * 0.01

    compounding_period = 2.
    if monthly:
        compounding_period = 12.
    return ((1.+(annual_rate_dec/compounding_period))**compounding_period)**(1./12)-1.

def calculate_payment(loan, annual_rate, loan_length_years, variable = False):
    monthly_rate = calculate_monthly_rate(annual_rate, monthly = variable)

    payment = (loan*monthly_rate)/(1-(1+monthly_rate)**(-loan_length_years*12.))

    return round(payment, 2)

def calculate_interest(annual_rate, balance, variable = False):
    monthly_rate = calculate_monthly_rate(annual_rate, monthly = variable)
    return round(balance * monthly_rate, 2)

# need to add extra payment schedule
def calculate_monthly_amortization(loan, rates, loan_length_years, term_length_years, extra_payments = [], variable = False):
    term_length_months = term_length_years * 12
    if variable:
        if len(rates) != term_length_months:
            print('error!')
    
    monthly_payment = calculate_payment(loan, rates[0], loan_length_years, variable = variable)
    payments = np.ones(term_length_months) * monthly_payment 

    if len(extra_payments) == 0:
        extra_payments = np.zeros(term_length_months)

    payments += extra_payments

    # these get an extra element for calculating start of term, we later pop it out
    interest_payments = [0]
    principal_payments = [0]
    balance = [loan] 

    for index, payment in enumerate(payments):
        interest = calculate_interest(rates[index], balance[index], variable = variable)
        principal = payment - interest 
        new_balance = balance[index] - principal

        interest_payments.append(interest)
        principal_payments.append(principal)
        balance.append(new_balance)

    output = {}
    output['payments'] = payments
    output['interest_payments'] = interest_payments[1:]
    output['principal_payments'] = principal_payments[1:]
    output['balance'] = balance[1:]

    return output

# todo: format this as a table instead, or in addition
# todo: make summary plots as well comparing the various options
def make_summary(outputs, labels):
    best_balance = 10000000000000
    best_label = 'None'

    worst_balance = 0
    worst_label = 'None'

    list_total_payments = []
    list_interest_payments = []
    list_principal_payments = []
    list_final_balance = []

    for output, label in zip(outputs, labels):
        total_payments = round(sum(output['payments']), 2)
        total_interest_payments = round(sum(output['interest_payments']), 2)
        total_principal_payments = round(sum(output['principal_payments']), 2)
        final_balance = output['balance'][-1]

        list_total_payments.append(total_payments)
        list_interest_payments.append(total_interest_payments)
        list_principal_payments.append(total_principal_payments)
        list_final_balance.append(final_balance)

        if final_balance < best_balance:
            best_balance = final_balance
            best_label = label
        if final_balance > worst_balance:
            worst_balance = final_balance
            worst_label = label

        output_string = f'For {label}, your final balance is {round(final_balance, 2)}. You paid {total_interest_payments} in interest and {total_principal_payments} in principal, for a principal fraction of {round(total_principal_payments / total_payments, 3)}\n'
        print(output_string)
    
    final_string = f'Out of the above choices, {best_label} has the best final balance, at {round(best_balance, 2)}. This gives {round(worst_balance - best_balance, 2)} of savings compared to the worst scenario, {worst_label}.'
    print(final_string)


    # comparison of payments
    X = np.arange(len(labels))
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 8)
    ax.set_xticks(X+0.25)
    ax.set_xticklabels(labels)
    rects1 = ax.bar(X + 0.00, list_total_payments, width = 0.25)
    rects2 = ax.bar(X + 0.25, list_interest_payments, width = 0.25)
    rects3 = ax.bar(X + 0.50, list_principal_payments, width = 0.25)


    plt.legend(['Total payments', 'Interest payments', 'Principal payments'])

    plt.show()  


    #comparison of balances
    fig = plt.figure()
    fig.set_size_inches(8, 6)
    ax = fig.add_axes([0,0,1,1])
    ax.bar(labels,list_final_balance)
    ax.set_ylabel('Balance')
    plt.show()

    #comparison of principal fraction
    fig = plt.figure()
    fig.set_size_inches(8, 6)
    ax = fig.add_axes([0,0,1,1])
    ax.bar(labels, [x / y for x, y in zip(list_principal_payments, list_total_payments)])
    ax.set_ylabel('Fraction of payments going to principal')
    plt.ylim([0, 1])
    plt.show()
