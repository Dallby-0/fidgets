export interface User {
  user_id: string;
  username: string;
  email: string;
}

export interface UserLogin {
  username_or_email: string;
  password: string;
  remember_me?: boolean;
}

export interface UserRegister {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

