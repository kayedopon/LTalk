
# LTalk - Language Learning Application
## Coursework Report for Object-Oriented Programming - Python App

### Introduction

**Purpose and Objectives of the Application**
LTalk is a comprehensive language learning application designed to help users build their vocabulary and improve language skills through various interactive exercises. The application provides a platform for creating, managing, and practicing word sets with different exercise types such as flashcards, multiple-choice questions, and fill-in-the-gap exercises.

**Brief Overview of Chosen Project**
The project implements a full-stack web application using Django, a Python web framework, with REST API capabilities for seamless frontend-backend communication. The application focuses on providing an engaging learning experience with progress tracking and personalized content.

### Problem Definition and Requirements

**Description of the Problem the Application Solves**
Language learning is often challenging due to the difficulty in maintaining consistent practice and effectively tracking progress. Traditional methods lack personalization and immediate feedback. LTalk addresses these challenges by providing:
- Personalized word set creation and management
- Various exercise types to accommodate different learning styles
- Progress tracking to help users visualize their improvement
- Interactive and engaging practice sessions

**Functional and Non-functional Requirements**

*Functional Requirements:*
- User authentication and account management
- Creation and management of word sets
- Multiple exercise types (flashcards, multiple-choice, fill-in-the-gap, text exercises)
- Progress tracking for words and exercises
- Exercise history and performance review
- Public/private word set visibility control
- Word set duplication functionality

*Non-functional Requirements:*
- Responsive and intuitive user interface
- Secure authentication and data protection
- High performance and scalability
- Cross-platform compatibility

### Design and Implementation

**Object-oriented Design Principles Used**

1. **Encapsulation**
   - The application encapsulates data and functionality within the `ExerciseViewSet` class, hiding implementation details and exposing only necessary logic through view methods.
   - Example: The `ExerciseViewSet` encapsulates question generation logic through private helper methods like `_generate_flashcard_data()` and `_get_unlearned_words()`, keeping the internal process hidden while allowing controlled use via `get_queryset()` and `perform_create()`.

2. **Inheritance**
   - The application utilizes inheritance to extend existing functionality and promote code reuse.
   - Example: The `User` class extends Django's `AbstractUser` class, inheriting authentication functionality while adding custom fields and methods.
   - The `CustomUserManager` extends Django's `UserManager` to implement custom user creation logic.

3. **Polymorphism**
   - The application implements polymorphism through method overriding and interfaces.
   - Example: The serializers in `api/serializer.py` override methods like `create()`, `update()`, and `validate()` to provide custom implementations while maintaining the same interface.
   - Different exercise types (flashcards, multiple-choice, fill-in-gap) share a common API but implement different behaviors.

4. **Abstraction**
   - Exercise creation and evaluation are abstracted through the `Exercise` model and API, hiding the complexity of generating questions and evaluating answers.

**Class Diagrams and Structure**

Key Model Classes:
1. **User** (from `authentication.models`)
   - Custom user model extending Django's AbstractUser
   - Attributes: username, email, is_active, is_superuser, is_staff, date_joined, last_login
   - Methods: __str__

2. **WordSet** (from `main.models`)
   - Attributes: user, title, description, public, created, duplicated_from
   - Methods: learned_percent, __str__
   - Relationships: belongs to User, contains many Words

3. **Word** (from `main.models`)
   - Attributes: word, infinitive, translation
   - Methods: __str__
   - Relationships: belongs to many WordSets

4. **WordProgress** (from `main.models`)
   - Attributes: user, word, correct_attempts, incorrect_attempts, is_learned
   - Methods: update_progress
   - Relationships: belongs to User and Word

5. **Exercise** (from `main.models`)
   - Attributes: wordset, type, questions, correct_answers
   - Methods: __str__
   - Relationships: belongs to WordSet

6. **ExerciseProgress** (from `main.models`)
   - Attributes: user, exercise, user_answer, is_correct, answered_at, grade
   - Methods: __str__
   - Relationships: belongs to User and Exercise

7. **SentenceTemplate** (from `main.models`)
   - Attributes: word, sentence, correct_form, created
   - Methods: __str__
   - Relationships: belongs to Word

**Design Patterns Implemented**

1. **MVT (Model-View-Template)**
   - The project uses Django's MVT (Model-View-Template) pattern to separate concerns.
   - Models handle database interactions, Views process user requests and business logic, and Templates render dynamic HTML for the user interface.
   - This ensures modularity and simplifies maintenance by keeping data, logic, and presentation layers distinct.

2. **Factory Method Pattern**
   - The `CustomUserManager` implements a factory method pattern with `create_user` and `_create_user` methods.
   - These methods handle the creation of User objects with appropriate default values and validations.

3. **Observer Pattern**
   - The progress tracking system implements an observer pattern where exercise attempts observe and update word progress.
   - When exercises are completed, the system updates the related `WordProgress` objects to reflect the user's performance.

4. **Strategy Pattern**
   - Different exercise types (flashcards, multiple-choice, fill-in-gap) implement the strategy pattern.
   - Each exercise type has its own implementation strategy for question generation and answer evaluation while sharing a common interface.

**Key Algorithms and Data Structures Implemented**

1. **Progress Calculation Algorithm**
   - The `WordProgress.update_progress` method implements an algorithm that calculates if a word is considered "learned" based on correct/incorrect attempts ratio.
   - The `WordSet.learned_percent` method calculates the percentage of learned words in a set.

2. **Fisher-Yates Shuffle Algorithm**
   - In the frontend JavaScript (flashcard.js), the application uses the Fisher-Yates shuffle algorithm to randomize questions for exercises.

3. **JSON Data Structure**
   - The application uses JSON data structures extensively for storing exercise questions, answers, and user responses.
   - This allows flexible data storage and exchange between frontend and backend.

4. **RESTful API Structure**
   - The application implements a RESTful API structure with serializers, views, and URL routing.
   - This structure provides a consistent and standardized way to interact with the application's resources.

### Development Process

**Tools and Environment**

The application was developed using a variety of tools and technologies:

1. **Backend Development**
   - Python 3.x as the primary programming language
   - Django web framework for server-side logic and ORM
   - Django REST Framework for API development
   - SQLite database for development

2. **Frontend Development**
   - HTML, CSS, and JavaScript for user interface
   - Django Templates for server-side rendering
   - Fetch API for AJAX communication with the backend

3. **Version Control and Deployment**
   - Git for version control
   - GitHub for code repository hosting
   - Docker for containerization and deployment

**Steps Followed During Development**

1. **Requirements Analysis**
   - Identified the core requirements for a language learning application
   - Defined the scope and features based on user needs

2. **Design Phase**
   - Created the data model design with entities and relationships
   - Designed the API structure and endpoints
   - Planned the user interface and experience

3. **Implementation**
   - Developed the authentication system with custom user model
   - Implemented the core models for word sets, words, and progress tracking
   - Created the API endpoints and serializers
   - Developed the frontend templates and JavaScript functionality
   - Implemented the exercise types and progress tracking

4. **Testing**
   - Conducted unit testing for models and APIs
   - Performed functional testing for user workflows
   - Implemented test cases as seen in `tests.py` files

5. **Deployment**
   - Created Docker configuration for containerization
   - Set up Nginx for serving static files and reverse proxy

### Results and Demonstration

**Application Features**

1. **User Authentication**
   - Custom user model with email-based authentication
   - Registration, login, and profile management

2. **Word Set Management**
   - Extracting words from photos using Gemini
   - Creation, editing, and deletion of word sets
   - Public/private visibility control
   - Word addition and removal

3. **Exercise Types**
   - Flashcards: Interactive cards showing word and translation
   - Multiple Choice: Select the correct translation from options
   - Fill-in-the-Gap: Complete sentences with appropriate words
   - Text Exercises: More complex language practice

4. **Progress Tracking**
   - Word-level progress tracking (learned vs. not learned)
   - Exercise history and performance review
   - Visual progress indicators

5. **Exploration**
   - Browse and discover public word sets from other users
   - Duplicate interesting word sets for personal use

### Testing and Validation

**Description of Testing Procedures**

1. **Unit Testing**
   - Implemented unit tests for models, views, and API endpoints
   - Tested model validation and constraints
   - Verified API responses and error handling

2. **Integration Testing**
   - Tested the interaction between different components
   - Verified data flow from frontend to backend and vice versa
   - Ensured proper state management and updates

3. **User Testing**
   - Conducted user testing sessions for usability feedback
   - Identified and addressed pain points in the user journey
   - Refined the interface based on user feedback

**Test Results and Issues Resolved**

1. **API Validation**
   - Improved input validation in serializers to prevent invalid data
   - Added comprehensive error messages for better debugging

2. **Exercise Generation**
   - Fixed issues with question generation for different exercise types
   - Implemented better shuffling algorithm for randomizing questions

3. **Progress Tracking**
   - Resolved issues with progress calculation and display
   - Fixed race conditions in simultaneous progress updates

4. **Security**
   - Implemented proper CSRF protection for API calls
   - Ensured secure handling of user authentication and data

### Conclusion and Future Work

**Summary of Achievements**

LTalk successfully implements a comprehensive language learning platform with robust features for vocabulary acquisition and practice. The application demonstrates strong adherence to object-oriented programming principles and design patterns, creating a maintainable and extensible codebase.

The key achievements include:
- Implementation of all four OOP pillars: encapsulation, inheritance, polymorphism, and abstraction
- Application of multiple design patterns for better code organization and reusability
- Creation of a user-friendly interface for language learning
- Implementation of a robust API for frontend-backend communication
- Effective progress tracking and performance evaluation

**Recommendations for Future Improvements**

1. **Content Enhancement**
   - Implement image associations for visual learners
   - Develop more advanced exercise types for grammar practice

2. **Social Features**
   - Add friend connections between users
   - Implement challenges and competitions
   - Create leaderboards and achievements

3. **AI Integration**
   - Implement AI-powered personalized learning paths
   - Create the chat with AI-assistant to get real-time advices
   - Use natural language processing for better sentence generation
   - Add intelligent difficulty adjustment based on user performance

4. **Data Analysis**
   - Implement more detailed analytics for learning patterns
   - Provide insights and recommendations based on performance data

5. **Gamification**
   - Add points, badges, and levels to increase engagement
   - Implement streaks and daily goals to encourage regular practice

The application successfully fulfills the requirements of reading from and writing to files through its database operations and file-based configurations. The project has been developed using Git version control, promoting collaborative development and proper code management.
