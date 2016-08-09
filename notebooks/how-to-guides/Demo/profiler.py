import pandas as pd
import seaborn as sns


import matplotlib.pyplot as plt
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def profile_attr_in_table(df, attribute, max_categories):
    out_df = pd.DataFrame(columns=['Property', 'Value'])


def profile_table(df, attribute, max_categories=15):
    out_df = pd.DataFrame(columns=['Property', 'Value'])
    unique_values = pd.unique(df[attribute])
    num_missing = sum(pd.isnull(df[attribute]))

    print('Number of unique values: %d' % len(unique_values))
    print('Number of missing values: %d' % num_missing)
    # unique_values

    if (len(unique_values) <= max_categories):
        print('\nUnique values: ')
        print(sorted(list(unique_values)))
        print('\nFrequency plot:\n')

        # ax = sns.barplot(x=attribute, y="index", data=(
        # pd.DataFrame(df[attribute].value_counts())).reset_index())
        # ax.set(xlabel='count', ylabel=Attribute)
        # ax.grid(b=True, which='major', color='w', linewidth=1.0)
        # plt.show()
        d = (pd.DataFrame(df[attribute].value_counts()))
        ax = sns.barplot(x="index", y=attribute, data=(
        pd.DataFrame(df[attribute].value_counts())).reset_index())
        ax.set(xlabel='count', ylabel=attribute)
        ax.grid(b=True, which='major', color='w', linewidth=1.0)
        ax.set_xticklabels(labels=d.index.values, rotation=90)
        plt.show()

        # g = sns.factorplot(attribute, data=df, aspect=2, kind="count",
        #                    color="b")
        # g.set_xticklabels(rotation=90)
        # # g.grid(b=True, which='major', color='w', linewidth=1.0)
        # plt.show()
