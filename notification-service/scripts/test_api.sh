#!/bin/bash

# API Test Script for Notification Service
# Tests all REST endpoints

BASE_URL="http://localhost:8080"
JWT_TOKEN="your-jwt-token-here"  # Replace with actual JWT token
USER_ID="user_123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if server is running
check_server() {
    print_header "Checking Server Health"
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
    
    if [ "$response" -eq 200 ]; then
        print_success "Server is healthy"
        return 0
    else
        print_error "Server is not responding (HTTP $response)"
        return 1
    fi
}

# Test: Get all notifications
test_get_notifications() {
    print_header "Test: Get All Notifications"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications?page=0&size=20")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Got notifications"
        echo "$body" | jq '.'
    else
        print_error "Failed to get notifications (HTTP $http_code)"
        echo "$body"
    fi
}

# Test: Get unread notifications only
test_get_unread_notifications() {
    print_header "Test: Get Unread Notifications"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications?page=0&size=20&unreadOnly=true")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Got unread notifications"
        echo "$body" | jq '.'
    else
        print_error "Failed to get unread notifications (HTTP $http_code)"
    fi
}

# Test: Get unread count
test_get_unread_count() {
    print_header "Test: Get Unread Count"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications/unread-count")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Got unread count"
        echo "$body" | jq '.'
    else
        print_error "Failed to get unread count (HTTP $http_code)"
    fi
}

# Test: Mark notification as read
test_mark_as_read() {
    print_header "Test: Mark Notification as Read"
    
    # First get a notification ID
    print_info "Getting notification ID..."
    notifications=$(curl -s \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications?page=0&size=1")
    
    notification_id=$(echo "$notifications" | jq -r '.notifications[0].id // empty')
    
    if [ -z "$notification_id" ]; then
        print_error "No notifications found to mark as read"
        return 1
    fi
    
    print_info "Marking notification $notification_id as read..."
    
    response=$(curl -s -w "\n%{http_code}" \
        -X PATCH \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications/$notification_id/read")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Marked notification as read"
        echo "$body" | jq '.'
    else
        print_error "Failed to mark as read (HTTP $http_code)"
    fi
}

# Test: Mark all as read
test_mark_all_as_read() {
    print_header "Test: Mark All Notifications as Read"
    
    response=$(curl -s -w "\n%{http_code}" \
        -X PATCH \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications/read-all")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Marked all notifications as read"
        echo "$body" | jq '.'
    else
        print_error "Failed to mark all as read (HTTP $http_code)"
    fi
}

# Test: Delete notification
test_delete_notification() {
    print_header "Test: Delete Notification"
    
    # First get a notification ID
    print_info "Getting notification ID..."
    notifications=$(curl -s \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications?page=0&size=1")
    
    notification_id=$(echo "$notifications" | jq -r '.notifications[0].id // empty')
    
    if [ -z "$notification_id" ]; then
        print_error "No notifications found to delete"
        return 1
    fi
    
    print_info "Deleting notification $notification_id..."
    
    response=$(curl -s -w "\n%{http_code}" \
        -X DELETE \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications/$notification_id")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Deleted notification"
        echo "$body" | jq '.'
    else
        print_error "Failed to delete notification (HTTP $http_code)"
    fi
}

# Test: Get statistics
test_get_statistics() {
    print_header "Test: Get Statistics"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications/statistics")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Got statistics"
        echo "$body" | jq '.'
    else
        print_error "Failed to get statistics (HTTP $http_code)"
    fi
}

# Test: Get preferences
test_get_preferences() {
    print_header "Test: Get User Preferences"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$BASE_URL/api/notifications/preferences")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Got preferences"
        echo "$body" | jq '.'
    else
        print_error "Failed to get preferences (HTTP $http_code)"
    fi
}

# Test: Update preferences
test_update_preferences() {
    print_header "Test: Update User Preferences"
    
    payload='{
        "notifications": {
            "like": true,
            "message": true,
            "profile-view": false,
            "friend-request": true,
            "friend-post": true
        },
        "emailNotifications": true,
        "pushNotifications": false,
        "quietHours": {
            "enabled": true,
            "start": "23:00",
            "end": "07:00"
        }
    }'
    
    response=$(curl -s -w "\n%{http_code}" \
        -X PATCH \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$BASE_URL/api/notifications/preferences")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Updated preferences"
        echo "$body" | jq '.'
    else
        print_error "Failed to update preferences (HTTP $http_code)"
        echo "$body"
    fi
}

# Test: Unauthorized access
test_unauthorized() {
    print_header "Test: Unauthorized Access (No Token)"
    
    response=$(curl -s -w "\n%{http_code}" \
        "$BASE_URL/api/notifications")
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -eq 401 ]; then
        print_success "Correctly rejected unauthorized request (HTTP 401)"
    else
        print_error "Did not reject unauthorized request (HTTP $http_code)"
    fi
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Notification Service API Test Menu   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
    echo "1.  Check Server Health"
    echo "2.  Get All Notifications"
    echo "3.  Get Unread Notifications"
    echo "4.  Get Unread Count"
    echo "5.  Mark Notification as Read"
    echo "6.  Mark All as Read"
    echo "7.  Delete Notification"
    echo "8.  Get Statistics"
    echo "9.  Get User Preferences"
    echo "10. Update User Preferences"
    echo "11. Test Unauthorized Access"
    echo "12. Run All Tests"
    echo "0.  Exit"
    echo ""
}

# Run all tests
run_all_tests() {
    print_header "Running All Tests"
    
    check_server || exit 1
    test_get_notifications
    test_get_unread_notifications
    test_get_unread_count
    test_mark_as_read
    test_mark_all_as_read
    test_get_statistics
    test_get_preferences
    test_update_preferences
    test_unauthorized
    
    print_header "All Tests Completed"
}

# Check dependencies
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed (optional but recommended)"
        print_info "Install with: sudo apt-get install jq  # or brew install jq"
    fi
}

# Main script
main() {
    check_dependencies
    
    print_header "Notification Service API Tester"
    print_info "Base URL: $BASE_URL"
    print_info "JWT Token: ${JWT_TOKEN:0:20}..."
    
    if [ "$1" == "--all" ]; then
        run_all_tests
        exit 0
    fi
    
    while true; do
        show_menu
        read -p "Enter your choice: " choice
        
        case $choice in
            1) check_server ;;
            2) test_get_notifications ;;
            3) test_get_unread_notifications ;;
            4) test_get_unread_count ;;
            5) test_mark_as_read ;;
            6) test_mark_all_as_read ;;
            7) test_delete_notification ;;
            8) test_get_statistics ;;
            9) test_get_preferences ;;
            10) test_update_preferences ;;
            11) test_unauthorized ;;
            12) run_all_tests ;;
            0) 
                print_info "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                ;;
        esac
        
        read -p "Press Enter to continue..."
    done
}

# Run main
main "$@"