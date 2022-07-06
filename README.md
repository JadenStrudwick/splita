# FEATURES

## MAIN FEATURES

- Secure user registration and authentication
  - User must confirm their password before their account can be created
  - Login page informs the user if their password is incorrect, or if the email they used does not have an account associated with it yet
  - Automatically signs the user in once account registration is complete

- User can create multiple households
  - Each household can be unique and contain different members
  - Bills are equally shared among all members of the household
  - Only the creator or "owner" of the household can delete the house, but any member of a house can leave at any time (and the bill splitting calculation will correctly display the new bill totals if a user leaves)

- User can add bills to specific households
  - Can track how much they owe individually, along with the total amount of the bill
  - Can see the payment status of all the other members in the household
  - Only the "owner" of the household can delete a bill prematurely, but anyone can pay a bill at any time
  - Paying a bill updates the website without requiring a refresh of the page (thanks to AJAX)
  - Bills automatically get deleted once every member of a household has paid it

- User receives notifications of new bills
  - Because a creation timestamp is associated with each bill, we can check if a bill has been added to a user's household since their last log in time
  - New bills are displayed in a small summary at the top of the dashboard page, giving the user the information they need to go to the respective bill and pay it

## EXTRA FEATURES

- Mobile compatibility
  - The text size and other styling attributes automatically scale with the height of the viewport, so on mobile devices the text and buttons become bigger
  - Scaling works dynamically across many viewport sizes (instead of suddenly changing once a viewport threshold is reached)
  - All pages are formatted such that they are pleasant to use on a mobile device

- Theme selector
  - User can choose their own primary theme colour within the settings menu
  - Colour preference is stored as a property of the user object and saved within the database
  - Javascript is used to retrieve this colour preference and dynamically alters a CSS variable to change the styling of the entire page
  - Default theme is pink, but if a user changes their preferred colour, the webapp will remember this choice for all future sessions

- Password updating
  - Within the settings menu, the user can update their password
  - Only updates the password if the old password is correct and the new password matches the "confirm password" field
  - Ensures the user can take the appropriate steps to secure their accounts

- Subset Splitting
  - Since multiple households can be created, a user can create another household with a subset of members from their main house
  - Allows the user to split miscellaneous payments such as dinners, etc

- Secure
  - Cross site scripting and SQL injection protected
  - User data is safe and well hidden from potential bad actors
