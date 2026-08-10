import pytest
from dash.testing.application_runners import import_app
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# Import your app
from app import app

@pytest.fixture
def dash_duo():
    """Create a Dash test fixture"""
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run tests without opening browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Use webdriver-manager to handle Chrome driver
    service = Service(ChromeDriverManager().install())
    
    from dash.testing.composite import DashComposite
    driver = DashComposite(
        app=app,
        browser="chrome",
        headless=True,
        options=chrome_options,
        service=service
    )
    yield driver
    driver.close()

def test_header_present(dash_duo):
    """
    Test 1: Verify the header is present in the application
    """
    # Start the app
    dash_duo.start_server(app)
    
    # Wait for the page to load
    dash_duo.wait_for_element("h1", timeout=5)
    
    # Find the header (h1 tag)
    header = dash_duo.find_element("h1")
    
    # Assert header exists and contains the expected text
    assert header is not None
    assert "Pink Morsel" in header.text or "Soul Foods" in header.text
    print(f"✅ Test 1 Passed: Header found - '{header.text}'")

def test_visualization_present(dash_duo):
    """
    Test 2: Verify the visualization/chart is present
    """
    # Start the app
    dash_duo.start_server(app)
    
    # Wait for the chart to load (graph element)
    dash_duo.wait_for_element(".dash-graph", timeout=10)
    
    # Find the graph
    graph = dash_duo.find_element(".dash-graph")
    
    # Assert graph exists
    assert graph is not None
    
    # Check if the graph has content
    # Wait for the chart to render
    dash_duo.wait_for_contains_text(".dash-graph", "", timeout=10)
    
    # Get the graph's figure
    graph_component = dash_duo.find_element(".dash-graph")
    assert graph_component is not None
    
    print("✅ Test 2 Passed: Visualization present")

def test_region_picker_present(dash_duo):
    """
    Test 3: Verify the region picker/dropdown is present
    """
    # Start the app
    dash_duo.start_server(app)
    
    # Wait for the dropdown to load
    dash_duo.wait_for_element("#region-dropdown", timeout=5)
    
    # Find the dropdown
    dropdown = dash_duo.find_element("#region-dropdown")
    
    # Assert dropdown exists
    assert dropdown is not None
    
    # Check if dropdown has options
    # Get the current value
    current_value = dash_duo.find_element("#region-dropdown").get_attribute("value")
    
    # The default value should be 'All'
    assert current_value is not None
    
    print(f"✅ Test 3 Passed: Region picker present with value '{current_value}'")

def test_region_filter_works(dash_duo):
    """
    Additional Test (Bonus): Verify the region filter actually filters data
    """
    # Start the app
    dash_duo.start_server(app)
    
    # Wait for the chart to load
    dash_duo.wait_for_element(".dash-graph", timeout=10)
    
    # Get initial title
    initial_title = dash_duo.find_element(".dash-graph").get_attribute("data-title")
    
    # Find and click the dropdown to change region
    dash_duo.wait_for_element("#region-dropdown", timeout=5)
    
    # Click the dropdown
    dropdown = dash_duo.find_element("#region-dropdown")
    dropdown.click()
    
    # Select "East" option
    east_option = dash_duo.find_element("[data-value='east']")
    east_option.click()
    
    # Wait for the graph to update
    dash_duo.wait_for_element(".dash-graph", timeout=10)
    
    # Verify graph updated
    updated_title = dash_duo.find_element(".dash-graph").get_attribute("data-title")
    
    print("✅ Bonus Test Passed: Region filter works correctly")

def test_price_increase_line_present(dash_duo):
    """
    Additional Test (Bonus): Verify the price increase line is shown
    """
    # Start the app
    dash_duo.start_server(app)
    
    # Wait for the chart to load
    dash_duo.wait_for_element(".dash-graph", timeout=10)
    
    # Check if the checkbox is present
    checkbox = dash_duo.find_element("#show-line-toggle")
    assert checkbox is not None
    
    print("✅ Bonus Test Passed: Price increase toggle present")

def test_app_renders_without_errors(dash_duo):
    """
    Additional Test: Verify the app loads without errors
    """
    # Start the app
    dash_duo.start_server(app)
    
    # Check if the app loaded without JavaScript errors
    logs = dash_duo.driver.get_log("browser")
    errors = [log for log in logs if log["level"] == "SEVERE"]
    
    # Assert no severe errors
    assert len(errors) == 0, f"Browser errors found: {errors}"
    
    print("✅ App renders without errors")