This project is a simple command line application that helps users to manage their personal finances by tracking income, expenses, and generating financial reports.

**Prerequisites**

  a)Installation of latest Version of Python 
  
  b)SQLite3,getpass,datetime libraries(These are already installed during python installation)

  This command line application provides a menu-driven interface

**MAIN MENU**

  1)Register
  
  2)Login
  
  3)Exit

**USER MENU**

  **1)Add Transaction** - The transaction will be added to the database upon specifying the transaction type(income/expense), category(salary/food/rent..), amount, date.If the transaction type is income, then transaction will be automatically saved into the database.If the transaction type is expense, then at first checking will be done to see if there is any budget that is set already set for that particular category in the month specified under date. If the expense exceeds the budget for that month under the category specified, then an alert will be generated and the transaction will not be added otherwise the transaction will be added to the database.

  **2)View Trasactions** - It displays all transactions for the logged-in user, categorized by type and date.
  
  **3)Update Transaction** - Unless there is a restriction of budget under expense category, any transaction can be updated by specifying it's ID, new transaction type/new category/new amount/new date.
  
  **4)Delete Transaction** - Any transaction can be deleted by specifying the ID.
  
  **5)Generate Report(Monthly/Yearly)** - Report can be generated for month / year upon requirement.It summarizes total income, total expenses, and calculates savings (income - expenses).
  
  **6)Set Budget** - Monthly budgets can be set for a specific category.
  
  **7)Check Budget** - The budget amount, category, month and year for which budget has been set can be checked by choosing this feature.
  
  **8)Logout** - This will aid in returning to the main menu.
  
