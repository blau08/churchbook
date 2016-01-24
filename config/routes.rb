Rails.application.routes.draw do

  devise_for :users do
    delete 'logout' => 'sessions#destroy', :as => :destroy_user_session
  end

  root 'students#index'
  resources :students
  resources :demographics
end
