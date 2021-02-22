=> 29-03-2019 - 12.0.2.2 : Create index file according to new formate, Improve manifest file.

>> 12.0.2.4 : Add branch for customer and product.

12.0.2.5 : MAke index mobile compatible format.

12.0.2.6 : Overwrite sale order records rules for personal and all orders.

12.0.2.7 : Overwrite all rules for all managers from allow branches to global.
-> also set allow branches in preferences for branch manager.
-> Add post init hook and update sale order rules for branch.


12.0.2.8 :
-> Remove POS from branch. 


12.0.2.9 :
-> Add branch field in picking type related to stock.warehouse and updated the rule from global to user's current branch only for branch user.

12.0.3.0 :
-> Call super in all possible methods.
-> Update context all for order lines like sale, purchase, invoice, move and bank statement lines.

Version: 12.0.3.1 | Date : 22/09/2020
-> Give option to select default branch in header and pass selected branch to the records.

Date 24/09/2020
version 12.0.3.2
issue solve:-
	- when user want to change branch they need to click two time otherwise need to reload manually.

12.0.3.3 (26-11-2020) : Fixed issue now only user will be able to see partner which are given in allow branch or own branch.
